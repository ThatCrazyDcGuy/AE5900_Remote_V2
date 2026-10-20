"""
AE5900 Remote - optionale Kamera (Monitoring des Geraets).

Bewusst OHNE OpenCV: Das Programm 'ffmpeg' (apt install ffmpeg) liest die USB-Webcam ueber Video4Linux2 und
liefert fertige JPEG-Bilder (MJPEG). Ohne Spiegelung werden die Bilder der Kamera nur durchgereicht
(-c:v copy, praktisch keine CPU-Last); mit H-/V-Flip kodiert ffmpeg sie neu.

ffmpeg laeuft nur, solange mindestens ein Browser den Stream offen hat (5 s Nachlauf). Ist die Kamera in
Setup & Sync nicht eingeschaltet, startet nichts und es entsteht kein Netzwerkverkehr.
Es werden nur Kameras mit MJPEG-Ausgabe unterstuetzt (praktisch jede USB-Webcam der letzten Jahre).
"""
import os
import re
import select
import shutil
import subprocess
import threading
import time
import collections

SYS_V4L = "/sys/class/video4linux"
BY_ID = "/dev/v4l/by-id"
# Interne Geraete des Raspberry Pi (Kamera-Pipeline, Video-Codec) sind keine USB-Webcams
SKIP_NAMES = ("bcm2835", "rpi-hevc", "rpivid", "pispbe", "unicam", "rp1-cfe", "-isp", "codec",
              "decoder", "encoder", "hevc", "vc4", "mem2mem")
RESOLUTIONS = ("320x240", "640x480", "1280x720")
DEFAULT_RES = "640x480"
IDLE_STOP_S = 5.0          # so lange laeuft ffmpeg nach dem letzten Zuschauer weiter
MAX_VIEWERS = 3            # Schutz fuer kleine Raspberry Pi
BOUNDARY = b"frame"


def ffmpeg_path():
    return shutil.which("ffmpeg")


def _num(name):
    m = re.search(r"(\d+)$", name)
    return int(m.group(1)) if m else 0


def list_cameras():
    """USB-Webcams als Liste von {'dev': stabiler Pfad, 'name': Anzeigename}.
    Pro Kamera gibt es meist zwei /dev/video*-Eintraege (Bild und Metadaten); nur 'index 0' ist die Bildquelle.
    Wo vorhanden wird der stabile Pfad aus /dev/v4l/by-id verwendet (bleibt nach Neustart/Umstecken gleich)."""
    result = []
    try:
        names = sorted([n for n in os.listdir(SYS_V4L) if re.fullmatch(r"video\d+", n)], key=_num)
    except OSError:
        return result
    by_id = {}
    try:
        for n in os.listdir(BY_ID):
            if n.endswith("-video-index0"):
                by_id[os.path.realpath(os.path.join(BY_ID, n))] = os.path.join(BY_ID, n)
    except OSError:
        pass
    for n in names:
        try:
            with open(os.path.join(SYS_V4L, n, "name"), encoding="utf-8", errors="replace") as f:
                label = f.read().strip()
        except OSError:
            label = n
        try:
            with open(os.path.join(SYS_V4L, n, "index")) as f:
                if f.read().strip() != "0":
                    continue
        except OSError:
            pass
        if any(s in label.lower() for s in SKIP_NAMES):
            continue
        dev = "/dev/" + n
        result.append({"dev": by_id.get(dev, dev), "name": label[:60]})
    return result


def valid_device(dev):
    return any(c["dev"] == dev for c in list_cameras())


def build_cmd(dev, res, hflip, vflip, fps):
    cmd = [ffmpeg_path() or "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin",
           "-f", "v4l2", "-input_format", "mjpeg", "-framerate", str(fps), "-video_size", res, "-i", dev]
    vf = []
    if hflip:
        vf.append("hflip")
    if vflip:
        vf.append("vflip")
    if vf:
        cmd += ["-vf", ",".join(vf), "-c:v", "mjpeg", "-q:v", "6"]
    else:
        cmd += ["-c:v", "copy", "-bsf:v", "mjpeg2jpeg"]
    cmd += ["-an", "-f", "image2pipe", "-"]
    return cmd


class CamStream:
    """Ein ffmpeg-Prozess fuer beliebig viele Zuschauer (max. MAX_VIEWERS)."""

    def __init__(self, get_cfg):
        self._get_cfg = get_cfg            # liefert ein dict mit den cam_*-Einstellungen
        self._cond = threading.Condition()
        self._lock = threading.Lock()
        self._viewers = 0
        self._thread = None
        self._frame = None
        self._seq = 0
        self.state = "idle"
        self._err = collections.deque(maxlen=3)

    # ------------------------------------------------------------------ Einstellungen
    def _settings(self):
        c = self._get_cfg()
        res = c.get("cam_res", DEFAULT_RES)
        if res not in RESOLUTIONS:
            res = DEFAULT_RES
        dev = c.get("cam_dev") or ""
        if not dev:
            cams = list_cameras()
            dev = cams[0]["dev"] if cams else ""
        try:
            fps = max(1, min(30, int(c.get("cam_fps", 10))))
        except (TypeError, ValueError):
            fps = 10
        return (dev, res, bool(c.get("cam_hflip")), bool(c.get("cam_vflip")), fps)

    def info(self):
        return {"state": self.state, "viewers": self._viewers}

    # ------------------------------------------------------------------ Zuschauer
    def acquire(self):
        with self._lock:
            if self._viewers >= MAX_VIEWERS:
                return False
            self._viewers += 1
            if self._thread is None or not self._thread.is_alive():
                self._thread = threading.Thread(target=self._run, daemon=True, name="cam-ffmpeg")
                self._thread.start()
        return True

    def release(self):
        with self._lock:
            self._viewers = max(0, self._viewers - 1)

    def frames(self):
        """Generator fuer die HTTP-Antwort (multipart/x-mixed-replace)."""
        if not self.acquire():
            return
        try:
            last = self._seq
            silent = 0.0
            while True:
                with self._cond:
                    got = self._cond.wait_for(lambda: self._seq != last, timeout=5.0)
                    frame, last = self._frame, self._seq
                if not got or frame is None:
                    silent += 5.0
                    if silent >= 20.0:     # Kamera liefert nichts mehr -> Verbindung beenden, Browser versucht es neu
                        return
                    continue
                silent = 0.0
                yield (b"--" + BOUNDARY + b"\r\nContent-Type: image/jpeg\r\nContent-Length: "
                       + str(len(frame)).encode() + b"\r\n\r\n" + frame + b"\r\n")
        finally:
            self.release()

    # ------------------------------------------------------------------ Worker
    def _publish(self, frame):
        with self._cond:
            self._frame = frame
            self._seq += 1
            self._cond.notify_all()

    def _stop_proc(self, proc):
        if proc is None:
            return
        try:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)
        except Exception:
            pass
        for s in (proc.stdout, proc.stderr):
            try:
                if s:
                    s.close()
            except Exception:
                pass

    def _drain_stderr(self, proc):
        try:
            for line in iter(proc.stderr.readline, b""):
                txt = line.decode("utf-8", "replace").strip()
                if txt:
                    self._err.append(txt[:160])
        except Exception:
            pass

    def _run(self):
        idle_since = None
        while True:
            with self._lock:
                viewers = self._viewers
            if viewers == 0:
                idle_since = idle_since or time.time()
                if time.time() - idle_since >= IDLE_STOP_S:
                    self.state = "idle"
                    self._frame = None
                    return
                time.sleep(0.3)
                continue
            idle_since = None

            sig = self._settings()
            dev, res, hflip, vflip, fps = sig
            if not ffmpeg_path():
                self.state = "ffmpeg not installed (sudo apt install ffmpeg)"
                time.sleep(2)
                continue
            if not dev or not valid_device(dev):
                self.state = "no camera found"
                time.sleep(2)
                continue

            self._err.clear()
            self._frame = None
            try:
                proc = subprocess.Popen(build_cmd(dev, res, hflip, vflip, fps), stdin=subprocess.DEVNULL,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except OSError as e:
                self.state = "cannot start ffmpeg: %s" % str(e)[:80]
                time.sleep(3)
                continue
            threading.Thread(target=self._drain_stderr, args=(proc,), daemon=True).start()
            self.state = "starting"
            buf = b""
            fd = proc.stdout.fileno()
            started = time.time()
            got_frame = False
            try:
                while True:
                    with self._lock:
                        viewers = self._viewers
                    if viewers == 0 and idle_since is None:
                        idle_since = time.time()
                    if viewers > 0:
                        idle_since = None
                    elif time.time() - idle_since >= IDLE_STOP_S:
                        break
                    if self._settings() != sig:       # Einstellung geaendert -> neu starten
                        break
                    if proc.poll() is not None:
                        break
                    if not got_frame and time.time() - started > 12:
                        self._err.append("no picture within 12 s (camera busy or not MJPEG?)")
                        break
                    r, _, _ = select.select([fd], [], [], 1.0)
                    if not r:
                        continue
                    chunk = os.read(fd, 65536)
                    if not chunk:
                        break
                    buf += chunk
                    while True:
                        s = buf.find(b"\xff\xd8")
                        if s < 0:
                            buf = buf[-1:]
                            break
                        e = buf.find(b"\xff\xd9", s + 2)
                        if e < 0:
                            if len(buf) > 3_000_000:       # Muell: verwerfen
                                buf = b""
                            else:
                                buf = buf[s:]
                            break
                        self._publish(buf[s:e + 2])
                        buf = buf[e + 2:]
                        got_frame = True
                        self.state = "streaming"
            finally:
                self._stop_proc(proc)
            if self._viewers == 0 and idle_since is not None and time.time() - idle_since >= IDLE_STOP_S:
                self.state = "idle"
                self._frame = None
                return
            if not got_frame or self._err:
                self.state = "error: " + (self._err[-1] if self._err else "camera stopped")
            time.sleep(2)
