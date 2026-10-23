"""
AE5900 Remote - Zugriffsschutz (Passwort, Anmelde-Cookie, API-Schluessel fuer PTT-Aufrufe anderer Programme).

Aufbau:
  * Das Passwort wird nie im Klartext gespeichert, nur als Hash in der config.json ("auth_hash").
  * Nach der Anmeldung bekommt der Browser ein signiertes Cookie (HttpOnly, SameSite=Strict, 30 Tage).
    Aendert sich das Passwort, werden alle alten Cookies ungueltig.
  * Falsche Passwoerter werden pro IP-Adresse gebremst (5 Fehlversuche, dann 30 s, 60 s, 120 s ... bis 15 min).
  * Ohne Passwort kann nur die Ersteinrichtung ausgefuehrt werden, und nur aus privaten Netzen (LAN, Tailscale, lokal).
  * "api_key": ein geheimer Schluessel, mit dem andere Programme (JS8Call, OpenWebRX-Knopf) ausschliesslich PTT
    ausloesen duerfen. Er schaltet nichts anderes frei.

Kommandozeile (z. B. bei vergessenem Passwort, Dienst vorher stoppen: systemctl --user stop ae5900):
    python3 ae_auth.py --set-password
    python3 ae_auth.py --show-key
"""
import argparse
import getpass
import hashlib
import hmac
import ipaddress
import json
import os
import secrets
import sys
import threading
import time

from itsdangerous import BadSignature, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

COOKIE_NAME = "ae5900_auth"
COOKIE_MAX_AGE = 30 * 24 * 3600       # 30 Tage
MIN_PW_LEN = 6
MAX_PW_LEN = 200
FREE_TRIES = 5                        # Fehlversuche ohne Wartezeit
BASE_DELAY_S = 30
MAX_DELAY_S = 900

_CGNAT = ipaddress.ip_network("100.64.0.0/10")     # Tailscale-IPv4-Adressen


# ----------------------------------------------------------------------------------------------- Adressen
def _ip(addr):
    try:
        ip = ipaddress.ip_address(addr)
    except (TypeError, ValueError):
        return None
    if ip.version == 6 and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    return ip


def is_loopback(addr):
    """True fuer Aufrufe vom Geraet selbst (127.0.0.1 / ::1), z. B. curl aus JS8Call auf dem Pi."""
    ip = _ip(addr)
    return bool(ip and ip.is_loopback)


def is_private_addr(addr):
    """True fuer lokale, private und Tailscale-Adressen. Eine Ersteinrichtung aus dem Internet wird abgelehnt."""
    ip = _ip(addr)
    if ip is None:
        return False
    return bool(ip.is_loopback or ip.is_private or ip.is_link_local or (ip.version == 4 and ip in _CGNAT))


# ----------------------------------------------------------------------------------------------- Hash
def hash_password(pw):
    try:
        return generate_password_hash(pw, method="scrypt:16384:8:1")
    except Exception:                                   # Python ohne scrypt-Unterstuetzung
        return generate_password_hash(pw, method="pbkdf2:sha256:260000")


def password_problem(pw):
    """None wenn das neue Passwort in Ordnung ist, sonst der Grund (englisch, wird im Browser angezeigt)."""
    if not isinstance(pw, str) or len(pw.strip()) < MIN_PW_LEN:
        return "The password needs at least %d characters." % MIN_PW_LEN
    if len(pw) > MAX_PW_LEN:
        return "The password is too long."
    return None


class AuthGuard:
    """cfg ist das (gemeinsam genutzte) config-dict des Programms, persist() schreibt es auf die Platte."""

    def __init__(self, cfg, persist):
        self.cfg = cfg
        self._persist = persist
        self._lock = threading.Lock()
        self._fails = {}                                # addr -> [Anzahl, gesperrt_bis, zuletzt]
        self.ensure_keys()

    # ------------------------------------------------------------------ Schluessel
    def ensure_keys(self):
        changed = False
        if not self.cfg.get("auth_secret"):
            self.cfg["auth_secret"] = secrets.token_hex(32)
            changed = True
        if not self.cfg.get("api_key"):
            self.cfg["api_key"] = secrets.token_urlsafe(18)
            changed = True
        if changed:
            self._persist()

    def new_api_key(self):
        self.cfg["api_key"] = secrets.token_urlsafe(18)
        self._persist()
        return self.cfg["api_key"]

    def key_ok(self, candidate):
        k = self.cfg.get("api_key") or ""
        return bool(k) and bool(candidate) and hmac.compare_digest(str(candidate), k)

    # ------------------------------------------------------------------ Passwort
    @property
    def configured(self):
        return bool(self.cfg.get("auth_hash"))

    def verify(self, pw):
        if not self.configured or not isinstance(pw, str):
            return False
        try:
            return check_password_hash(self.cfg["auth_hash"], pw)
        except Exception:
            return False

    def set_password(self, pw):
        """Setzt das Passwort. Gibt None zurueck oder den Grund der Ablehnung."""
        problem = password_problem(pw)
        if problem:
            return problem
        self.cfg["auth_hash"] = hash_password(pw)
        self._persist()
        return None

    # ------------------------------------------------------------------ Cookie
    def _ser(self):
        return URLSafeTimedSerializer(self.cfg["auth_secret"], salt="ae5900-login")

    def _fp(self):
        return hashlib.sha256(self.cfg.get("auth_hash", "").encode("utf-8")).hexdigest()[:16]

    def make_token(self):
        return self._ser().dumps({"f": self._fp()})

    def token_ok(self, token):
        if not token or not self.configured:
            return False
        try:
            data = self._ser().loads(token, max_age=COOKIE_MAX_AGE)
        except BadSignature:                            # schliesst SignatureExpired ein
            return False
        return isinstance(data, dict) and hmac.compare_digest(str(data.get("f", "")), self._fp())

    # ------------------------------------------------------------------ Bremse gegen Durchprobieren
    def wait_time(self, addr):
        """Sekunden, die diese Adresse noch warten muss (0 = darf es versuchen)."""
        with self._lock:
            rec = self._fails.get(addr)
            if not rec:
                return 0
            return max(0, int(rec[1] - time.time() + 0.999))

    def register_failure(self, addr):
        now = time.time()
        with self._lock:
            if len(self._fails) > 500:                  # alte Eintraege aufraeumen
                for a in [a for a, r in self._fails.items() if now - r[2] > 3600 and r[1] < now]:
                    self._fails.pop(a, None)
            rec = self._fails.setdefault(addr, [0, 0.0, now])
            rec[0] += 1
            rec[2] = now
            if rec[0] >= FREE_TRIES:
                rec[1] = now + min(MAX_DELAY_S, BASE_DELAY_S * (2 ** (rec[0] - FREE_TRIES)))
            return rec[0]

    def register_success(self, addr):
        with self._lock:
            self._fails.pop(addr, None)


# ----------------------------------------------------------------------------------------------- Kommandozeile
def _load(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("config.json has an unexpected format")
    return data


def _save(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        f.flush()
        os.fsync(f.fileno())
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    os.replace(tmp, path)


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="AE5900 Remote - set the web password / show the PTT key")
    ap.add_argument("--config", default=os.path.join(here, "config.json"), help="path of config.json")
    ap.add_argument("--set-password", action="store_true", help="set (or change) the web password")
    ap.add_argument("--show-key", action="store_true", help="show the API key for PTT calls of other programs")
    args = ap.parse_args(argv)
    if not (args.set_password or args.show_key):
        ap.print_help()
        return 2
    try:
        data = _load(args.config)
    except (OSError, ValueError) as e:
        print("Cannot read %s: %s" % (args.config, e))
        return 1
    changed = False
    if not data.get("auth_secret"):
        data["auth_secret"] = secrets.token_hex(32)
        changed = True
    if not data.get("api_key"):
        data["api_key"] = secrets.token_urlsafe(18)
        changed = True
    if args.set_password:
        for _ in range(3):
            p1 = getpass.getpass("New web password (at least %d characters): " % MIN_PW_LEN)
            problem = password_problem(p1)
            if problem:
                print(problem)
                continue
            if p1 != getpass.getpass("Repeat the password: "):
                print("The two entries differ.")
                continue
            data["auth_hash"] = hash_password(p1)
            changed = True
            print("Password set. Restart the program so that it takes effect:  systemctl --user restart ae5900")
            break
        else:
            print("No password set.")
            return 1
    if args.show_key:
        print("API key: " + data["api_key"])
    if changed:
        try:
            _save(args.config, data)
        except OSError as e:
            print("Cannot write %s: %s" % (args.config, e))
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
