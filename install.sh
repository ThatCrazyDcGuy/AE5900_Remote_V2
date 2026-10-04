#!/bin/bash
# =========================================================================
# AE5900 REMOTE CONTROLLER - SYSTEM INSTALLER
# Raspberry Pi OS (Bookworm/Trixie), Debian, Ubuntu
#
# Aufruf:  ./install.sh [Optionen]     (siehe ./install.sh --help)
# Der Installer ist wiederholbar: er repariert/ergaenzt nur, was fehlt.
# Log: ~/ae5900-install.log
# =========================================================================

set -o pipefail

GREEN='\033[0;32m'; BLUE='\033[0;34m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'

usage() {
cat <<'EOF'
AE5900 Remote Controller - installer

Usage: ./install.sh [options]

  --with-mumble          also install the Mumble client + server (optional - WebAudio does not need it)
  --no-tailscale         skip Tailscale (HTTPS, phone microphone and wake lock need it;
                         plain HTTP on port 5000 works without)
  --no-service           do not set up the autostart service (start by hand: python3 ae_5900_v2.py)
  --keep-onboard-audio   do not change the Raspberry Pi onboard audio settings (config.txt)
  --upgrade              run 'apt full-upgrade' first (slow, off by default)
  --yes                  never ask questions (automatic when there is no terminal)
  -h, --help             show this help

Safe to run again - it only repairs/updates what is missing.
Log file: ~/ae5900-install.log
EOF
}

WITH_MUMBLE=0; NO_TAILSCALE=0; NO_SERVICE=0; KEEP_ONBOARD=0; DO_UPGRADE=0; ASSUME_YES=0
for arg in "$@"; do
    case "$arg" in
        --with-mumble)         WITH_MUMBLE=1 ;;
        --no-tailscale)        NO_TAILSCALE=1 ;;
        --no-service)          NO_SERVICE=1 ;;
        --keep-onboard-audio)  KEEP_ONBOARD=1 ;;
        --upgrade)             DO_UPGRADE=1 ;;
        --yes|-y)              ASSUME_YES=1 ;;
        -h|--help)             usage; exit 0 ;;
        *) echo "Unknown option: $arg"; echo "Try: ./install.sh --help"; exit 2 ;;
    esac
done

USER_NAME="${USER:-$(id -un)}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$HOME/ae5900-install.log"
CONFIG_TXT="${AE_CONFIG_TXT:-/boot/firmware/config.txt}"   # ueberschreibbar fuer Tests
STATE_DIR="$HOME/.config/ae5900"
WARNINGS=()
INTERACTIVE=0
if [ -t 0 ] && [ "$ASSUME_YES" -eq 0 ]; then INTERACTIVE=1; fi

# Alle Ausgaben zusaetzlich ins Log - wenn jemand um Hilfe bittet, genuegt diese Datei.
exec > >(tee -a "$LOG") 2>&1

step() { echo -e "\n${BLUE}[$1] $2${NC}"; }
ok()   { echo -e "${GREEN}  [ok]${NC} $*"; }
info() { echo -e "  [i] $*"; }
warn() { echo -e "${YELLOW}  [!] $*${NC}"; WARNINGS+=("$*"); }
fail() { echo -e "${RED}  [X] $*${NC}"; echo "      Details are in the log: $LOG"; exit 1; }

# Schreibt stdin nach <pfad>; eine bereits vorhandene, abweichende Datei wird einmalig als .ae5900.bak gesichert.
write_file() {
    local path="$1" tmp
    tmp="$(mktemp)"; cat > "$tmp"
    mkdir -p "$(dirname "$path")"
    if [ -f "$path" ] && ! cmp -s "$tmp" "$path"; then cp -n "$path" "$path.ae5900.bak" 2>/dev/null; fi
    mv "$tmp" "$path"; chmod 644 "$path"
}

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}   AE5900 Remote Controller - System Installer      ${NC}"
echo -e "${BLUE}====================================================${NC}"
echo "Started: $(date)   |   Project folder: $PROJECT_DIR"

# -------------------------------------------------------------------------
step "0/8" "Pre-flight checks"
[ "$(id -u)" -ne 0 ] || fail "Please run this as a normal user - not as root and not with 'sudo ./install.sh'."
command -v apt-get >/dev/null 2>&1 || fail "This installer needs a Debian-based system (Raspberry Pi OS, Debian, Ubuntu)."
[ -f "$PROJECT_DIR/ae_5900_v2.py" ] || fail "ae_5900_v2.py not found next to install.sh. Run the installer from inside the project folder."
sudo -v || fail "sudo is required (you will be asked for your password)."
ok "System looks fine."

# -------------------------------------------------------------------------
step "1/8" "Updating package sources"
APT="sudo env DEBIAN_FRONTEND=noninteractive apt-get"
$APT update || fail "'apt update' failed - please check your internet connection."
if [ "$DO_UPGRADE" -eq 1 ]; then
    info "Running a full system upgrade (this can take a long time)..."
    $APT full-upgrade -y || warn "'apt full-upgrade' reported errors - continuing."
fi

# -------------------------------------------------------------------------
step "2/8" "Installing packages"
CRITICAL_PKGS=(git curl openssl python3 python3-flask python3-flask-socketio python3-socketio \
    python3-pyaudio python3-numpy python3-serial portaudio19-dev \
    pipewire pipewire-alsa pipewire-pulse wireplumber pulseaudio-utils dbus-user-session)
OPTIONAL_PKGS=(python3-eventlet python3-build python3-pip pipewire-audio pipewire-audio-client-libraries \
    libpipewire-0.3-modules ladspa-sdk swh-plugins pavucontrol openssh-server libhamlib-utils jq mc htop)

$APT install -y "${CRITICAL_PKGS[@]}" || fail "Installing the required packages failed (details in the log)."
ok "Required packages installed."
if ! $APT install -y "${OPTIONAL_PKGS[@]}"; then
    info "Some optional packages are not available - trying them one by one..."
    for pkg in "${OPTIONAL_PKGS[@]}"; do
        $APT install -y "$pkg" >/dev/null 2>&1 || warn "Optional package '$pkg' could not be installed (continuing without it)."
    done
fi
$APT remove -y pipewire-media-session >/dev/null 2>&1 || true   # altes Session-Modul, kollidiert mit WirePlumber

# -------------------------------------------------------------------------
step "3/8" "User groups and folders"
sudo usermod -a -G audio,dialout "$USER_NAME" \
    || warn "Could not add '$USER_NAME' to the groups 'audio' and 'dialout' (needed for sound card and serial port)."
mkdir -p "$PROJECT_DIR/ARC" "$STATE_DIR"
ok "Groups set (a re-login or reboot is needed for them to take effect)."

# -------------------------------------------------------------------------
step "4/8" "Audio configuration"
write_file "$HOME/.config/pipewire/pipewire.conf.d/custom.conf" <<'EOF'
context.properties = {
    default.clock.rate = 48000
    default.clock.allowed-rates = [ 44100 48000 88200 96000 ]
}
EOF
ok "PipeWire clock configured."

if [ ! -f "$HOME/.config/pavucontrol.ini" ]; then
    write_file "$HOME/.config/pavucontrol.ini" <<'EOF'
[window]
width=800
height=400
sinkInputType=1
sourceOutputType=1
sinkType=0
sourceType=1
showVolumeMeters=1
EOF
fi

# Raspberry Pi: Onboard-Audio abschalten, damit die USB-Soundkarte der einzige Audio-Weg ist
if [ "$KEEP_ONBOARD" -eq 1 ]; then
    info "Leaving the Raspberry Pi onboard audio settings untouched (--keep-onboard-audio)."
elif [ -f "$CONFIG_TXT" ]; then
    sudo cp -n "$CONFIG_TXT" "$CONFIG_TXT.ae5900.bak" 2>/dev/null
    sudo sed -i 's/^dtparam=audio=on/#dtparam=audio=on/' "$CONFIG_TXT"
    grep -q '^dtparam=audio=off' "$CONFIG_TXT" || echo 'dtparam=audio=off' | sudo tee -a "$CONFIG_TXT" >/dev/null
    grep -q '^dtoverlay=vc4-kms-v3d,noaudio' "$CONFIG_TXT" || echo 'dtoverlay=vc4-kms-v3d,noaudio' | sudo tee -a "$CONFIG_TXT" >/dev/null
    ok "Onboard audio disabled in $CONFIG_TXT (backup: $CONFIG_TXT.ae5900.bak). Takes effect after a reboot."
else
    info "No Raspberry Pi boot configuration found - skipping the onboard audio setting."
fi

# -------------------------------------------------------------------------
step "5/8" "Tailscale (HTTPS for phone microphone and wake lock)"

ts_state() {
    local j
    j="$(tailscale status --json 2>/dev/null)" || return 0
    if command -v jq >/dev/null 2>&1; then
        printf '%s' "$j" | jq -r '.BackendState // empty' 2>/dev/null
    else
        printf '%s' "$j" | grep -o '"BackendState": *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/'
    fi
}
ts_domain() {
    local j d
    j="$(tailscale status --self --json 2>/dev/null)" || return 0
    if command -v jq >/dev/null 2>&1; then
        d="$(printf '%s' "$j" | jq -r '.Self.DNSName // empty' 2>/dev/null)"
    else
        d="$(printf '%s' "$j" | grep -o '"DNSName": *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/')"
    fi
    printf '%s' "${d%.}"
}

TS_DOMAIN=""; HTTPS_READY=0
if [ "$NO_TAILSCALE" -eq 1 ]; then
    info "Skipping Tailscale (--no-tailscale). Control and listening work over HTTP on port 5000."
else
    if ! command -v tailscale >/dev/null 2>&1; then
        info "Installing Tailscale..."
        curl -fsSL https://tailscale.com/install.sh | sh || warn "Tailscale could not be installed - HTTPS will not be available."
    fi
    if command -v tailscale >/dev/null 2>&1; then
        if [ "$(ts_state)" != "Running" ]; then
            if [ "$INTERACTIVE" -eq 1 ]; then
                info "Tailscale needs a login. Open the link shown below in a browser (you have 3 minutes)."
                sudo timeout 180 tailscale up || true
            else
                warn "Tailscale is not logged in. Run 'sudo tailscale up' later, then run this installer again."
            fi
        fi
        if [ "$(ts_state)" = "Running" ]; then
            # Damit die App das Zertifikat spaeter selbst erneuern darf (ohne sudo-Passwort im Dienst)
            sudo tailscale set --operator="$USER_NAME" >/dev/null 2>&1 || true
            TS_DOMAIN="$(ts_domain)"
            if [ -n "$TS_DOMAIN" ]; then
                info "Tailscale name of this machine: $TS_DOMAIN"
                if [ -f "$PROJECT_DIR/$TS_DOMAIN.crt" ] && [ -f "$PROJECT_DIR/$TS_DOMAIN.key" ] \
                   && openssl x509 -checkend 1209600 -noout -in "$PROJECT_DIR/$TS_DOMAIN.crt" >/dev/null 2>&1; then
                    ok "A valid HTTPS certificate already exists."
                    HTTPS_READY=1
                elif ( cd "$PROJECT_DIR" && sudo tailscale cert "$TS_DOMAIN" ); then
                    sudo chown "$USER_NAME:" "$PROJECT_DIR/$TS_DOMAIN.crt" "$PROJECT_DIR/$TS_DOMAIN.key" 2>/dev/null
                    chmod 644 "$PROJECT_DIR/$TS_DOMAIN.crt"; chmod 600 "$PROJECT_DIR/$TS_DOMAIN.key"
                    ok "HTTPS certificate issued for $TS_DOMAIN."
                    HTTPS_READY=1
                else
                    warn "No HTTPS certificate yet. In the Tailscale admin console (https://login.tailscale.com/admin/dns) enable 'MagicDNS' and 'HTTPS Certificates'. The app retries automatically when it starts."
                fi
            else
                warn "Could not determine the Tailscale name of this machine."
            fi
        fi
    fi
fi

# -------------------------------------------------------------------------
step "6/8" "Mumble (optional)"
if [ "$WITH_MUMBLE" -eq 0 ]; then
    info "Not installed - the web audio does not need it. Add it any time with: ./install.sh --with-mumble"
else
    $APT install -y mumble mumble-server || warn "Mumble could not be installed completely."

    # PipeWire-Regeln: Mumble darf die Eingangslautstaerke nicht per Auto-Gain veraendern
    write_file "$HOME/.config/pipewire/pipewire-pulse.conf.d/99-disable-autogain.conf" <<'EOF'
pulse.rules = [
    {
        matches = [
            { application.process.binary = "mumble" }
            { application.process.binary = "mumble-worker" }
        ]
        actions = { quirks = [ block-source-volume ] }
    }
]
EOF
    write_file "$HOME/.config/pipewire/pipewire-pulse.conf.d/block-autoscale.conf" <<'EOF'
pulse.rules = [
    {
        matches = [ { application.process.binary = "mumble" } ];
        actions = { quirks = [ block-source-volume ] }
    }
]
EOF

    # Mumble-Voreinstellungen nur anlegen, wenn es noch keine gibt (nichts ueberschreiben)
    if [ ! -f "$HOME/.config/Mumble/Mumble/mumble_settings.json" ]; then
        write_file "$HOME/.config/Mumble/Mumble/mumble_settings.json" <<EOF
{
    "audio": {
        "cue_volume": 0.0009765625,
        "echo_cancel_mode": "Disabled",
        "external_applications_volume": 1.0,
        "input_system": "PulseAudio",
        "loudness": 20000,
        "noise_cancel_mode": "Off",
        "notification_volume": 0.0009765625,
        "output_delay": 1,
        "output_system": "PulseAudio",
        "transmit_mode": "Continuous",
        "vad_max": 0.9800103902816772,
        "vad_min": 0.8000122308731079
    },
    "last_connection": {
        "server_name": "ae5900ctrl",
        "username": "ae5900"
    },
    "misc": {
        "audio_wizard_has_been_shown": true,
        "database_location": "$HOME/.local/share/Mumble/Mumble/mumble.sqlite",
        "viewed_server_ping_consent_message": true
    },
    "mumble_has_quit_normally": true,
    "network": {
        "auto_connect_to_last_server": true,
        "frames_per_packet": 1
    },
    "settings_version": 1,
    "tts": { "tts_volume": 0 }
}
EOF
    fi
    mkdir -p "$HOME/.local/share/Mumble/Mumble/"; touch "$HOME/.local/share/Mumble/Mumble/mumble.sqlite"

    write_file "$HOME/.config/autostart/ae5900-mumble.desktop" <<'EOF'
[Desktop Entry]
Name=Mumble (AE5900)
Exec=mumble mumble://ae5900ADM@127.0.0.1:64738
Icon=mumble
Type=Application
EOF
    ok "Mumble installed and set to start with the desktop."

    # Einmaliger Erststart (Datenbank/Zertifikat bestaetigen) - nur mit Terminal+Desktop, mit Zeitlimit statt Endlos-Sperre
    if [ "$INTERACTIVE" -eq 1 ] && [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]; then
        echo "  Mumble can run once now to finish its own setup: confirm its questions, then close Mumble."
        if read -r -t 60 -p "  Press ENTER to start Mumble (skips by itself after 60 seconds)... " _; then
            timeout 300 mumble "mumble://ae5900ADM@127.0.0.1:64738" || true
        else
            echo; info "Skipped - start Mumble once by hand later."
        fi
    fi
fi

# -------------------------------------------------------------------------
step "7/8" "Autostart service"
if [ "$NO_SERVICE" -eq 1 ]; then
    info "Skipping the service (--no-service). Start the app by hand: python3 $PROJECT_DIR/ae_5900_v2.py"
else
    # Alte Installation (Terminal-Autostart + Starter-Skript) ersetzen, sonst startet die App doppelt
    OLD_DESKTOP="$HOME/.config/autostart/ae5900start.desktop"
    if [ -f "$OLD_DESKTOP" ]; then
        mv "$OLD_DESKTOP" "$OLD_DESKTOP.old" && info "Old terminal autostart disabled (kept as ae5900start.desktop.old)."
        info "Mumble no longer starts automatically - add it back with: ./install.sh --with-mumble"
    fi
    [ -f /usr/local/bin/ae5900starter ] && sudo mv /usr/local/bin/ae5900starter /usr/local/bin/ae5900starter.old

    PYTHON3="$(command -v python3)"
    UNIT_DIR="$HOME/.config/systemd/user"
    write_file "$UNIT_DIR/ae5900.service" <<EOF
[Unit]
Description=AE5900 Remote Controller
After=pipewire.service pipewire-pulse.service wireplumber.service
Wants=pipewire.service pipewire-pulse.service wireplumber.service

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR
Environment=PYTHONUNBUFFERED=1
# Kurze Wartezeit, damit PipeWire/WirePlumber die USB-Soundkarte nach dem Booten schon bereitstellen
ExecStartPre=/bin/sleep 8
ExecStart=$PYTHON3 $PROJECT_DIR/ae_5900_v2.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
    # Aktivieren per Symlink - funktioniert auch ohne laufende systemd-Benutzersitzung (z.B. per SSH)
    mkdir -p "$UNIT_DIR/default.target.wants"
    ln -sf ../ae5900.service "$UNIT_DIR/default.target.wants/ae5900.service"
    sudo loginctl enable-linger "$USER_NAME" || warn "Could not enable 'linger' - the service would only start after you log in."
    ok "Service 'ae5900' set up - it starts at boot and restarts itself after a crash."

    if systemctl --user daemon-reload >/dev/null 2>&1; then
        if systemctl --user is-active --quiet ae5900.service; then
            systemctl --user restart ae5900.service && ok "Service restarted with the current files."
        fi
    else
        info "No systemd user session reachable from this shell - the service starts at the next boot."
    fi
    if pgrep -f "[a]e_5900_v2.py" >/dev/null 2>&1 && ! systemctl --user is-active --quiet ae5900.service 2>/dev/null; then
        warn "The app is currently running outside the service. Stop it with 'pkill -f ae_5900_v2.py' - after the reboot the service takes over."
    fi
fi

# -------------------------------------------------------------------------
step "8/8" "Self-test"
MISSING="$(python3 - <<'PY' 2>/dev/null
import importlib
bad = []
for m in ("flask", "flask_socketio", "numpy", "pyaudio", "serial"):
    try:
        importlib.import_module(m)
    except Exception as e:
        bad.append("%s (%s)" % (m, e.__class__.__name__))
print(", ".join(bad))
PY
)"
if [ -z "$MISSING" ]; then ok "Python modules: all present."; else warn "Python modules missing or broken: $MISSING"; fi

if pactl info >/dev/null 2>&1; then
    SOURCES="$(pactl list short sources 2>/dev/null)"
    if echo "$SOURCES" | grep -q "alsa_input\.usb"; then
        ok "USB sound card with a recording input detected."
        # Die App findet die Karte nach ROLLE (USB-Geraet mit Ausgabe und Eingang), nicht nach Hersteller- oder Profilnamen.
        if [ "$(echo "$SOURCES" | grep -c "alsa_input\.usb")" -gt 1 ]; then
            info "Several USB audio devices found. If the wrong one is used, put part of the card's name into \"audio_card_match\" in config.json (the app logs the chosen card as '[AUDIO-ROUTING] Karte: ...')."
        fi
    elif echo "$SOURCES" | grep -qi "usb"; then
        warn "A USB audio device was found, but it has no recording input. The radio audio needs a USB sound card WITH an input (microphone / line-in)."
    else
        warn "No USB sound card detected - plug it in (and reboot once if PipeWire was just installed)."
    fi
else
    info "The audio server is not reachable from this session yet - it starts after a reboot."
fi

if ls /dev/ttyUSB* /dev/ttyACM* >/dev/null 2>&1; then ok "Serial port found: $(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | tr '\n' ' ')"
else info "No serial adapter found right now - connect the radio cable before starting the app."; fi

mkdir -p "$STATE_DIR"
{ date; echo "options: mumble=$WITH_MUMBLE tailscale_skipped=$NO_TAILSCALE service_skipped=$NO_SERVICE"; } > "$STATE_DIR/installed"

# -------------------------------------------------------------------------
IP_ADDR="$(hostname -I 2>/dev/null | awk '{print $1}')"
echo -e "\n${BLUE}=========================================================================${NC}"
echo -e "${GREEN}  Installation finished.${NC}"
if [ "${#WARNINGS[@]}" -gt 0 ]; then
    echo -e "${YELLOW}  Please note (${#WARNINGS[@]}):${NC}"
    for w in "${WARNINGS[@]}"; do echo -e "${YELLOW}   - $w${NC}"; done
fi
echo -e "${BLUE}=========================================================================${NC}"
echo "  1. Reboot once:   sudo reboot      (group changes, audio settings and the service start)"
echo "  2. Then open:     http://${IP_ADDR:-<ip-of-this-pi>}:5000"
if [ "$HTTPS_READY" -eq 1 ]; then
    echo "     With HTTPS (microphone, wake lock):  https://$TS_DOMAIN:5443"
elif [ -n "$TS_DOMAIN" ]; then
    echo "     HTTPS is not set up yet (see the note above) - control and listening work over HTTP."
fi
echo
echo "  Service status:   systemctl --user status ae5900"
echo "  Live log:         journalctl --user -u ae5900 -f"
echo "  Install log:      $LOG"
echo -e "${BLUE}=========================================================================${NC}"
