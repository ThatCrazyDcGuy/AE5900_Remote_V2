import eventlet
eventlet.monkey_patch()

import warnings
warnings.filterwarnings("ignore", message=".*RLock.*were not greened.*")

import time
import struct
from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit, join_room
import pymumble_py3 as pymumble

from flask.ctx import RequestContext
if not hasattr(RequestContext, "session") or not hasattr(RequestContext.session, "fset") or RequestContext.session.fset is None:
    RequestContext.session = property(
        lambda self: getattr(self, "_session", None),
        lambda self, value: setattr(self, "_session", value)
    )

app = Flask(__name__)

# AUS VERSION 2: Nur echte, schnelle WebSockets erlauben – das killt den Payload-Log-Stau!
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', transports=['websocket'])

# --- CONFIG FOR MUMBLE ---
MUMBLE_HOST = "127.0.0.1"
MUMBLE_PORT = 64738
BOT_NAME = "WebUI-Audio-Bridge"

mumble = None

def audio_receiver_loop():
    """ Holt 48kHz, dampft auf 16kHz fuer mobile Netze runter und streamt zum Browser """
    global mumble
    GAIN_FACTOR = 1.0 
    
    while True:
        if mumble and mumble.is_alive():
            for user in list(mumble.users.values()):
                if user['name'] == BOT_NAME:
                    continue
                
                while user.sound.is_sound():
                    sound_packet = user.sound.get_sound()
                    if sound_packet and sound_packet.pcm:
                        fmt = f"{len(sound_packet.pcm) // 2}h"
                        samples = struct.unpack(fmt, sound_packet.pcm)
                        
                        mod_samples = []
                        for s in samples[::3]:
                            val = int(s * GAIN_FACTOR)
                            val = max(-32768, min(32767, val))
                            mod_samples.append(val)
                            
                        fmt_low = f"{len(mod_samples)}h"
                        reduced_pcm = struct.pack(fmt_low, *mod_samples)
                        
                        socketio.emit('audio_out', reduced_pcm, room='audio_room')
        time.sleep(0.02)

eventlet.spawn(audio_receiver_loop)

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AE5900 Remote - Audio Bridge</title>
        <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
        <style>
            body { background: #111; color: #fff; font-family: sans-serif; text-align: center; padding-top: 50px; }
            .btn { background: #00ff00; color: black; border: none; padding: 15px 30px; font-size: 18px; cursor: pointer; border-radius: 5px; font-weight: bold; }
            .btn.off { background: #ff3333; color: white; }
            #status { margin-top: 20px; color: #888; }
        </style>
    </head>
    <body>
        <h1>Albrecht AE 5900 - Mumble Audio Tab</h1>
        <hr style="width: 300px; border-color: #333;">
        <br>
        <button id="audioBtn" class="btn off" onclick="toggleAudio()">AUDIO RECV: OFF</button>
        <div id="status">Warte auf Verbindung...</div>

        <script>
            // AUS VERSION 2: Browser starr auf WebSocket pinnen
            const socket = io({ transports: ['websocket'], upgrade: false });
            let audioContext = null;
            let isAudioOn = false;
            
            let nextStartTime = 0;
            const BUFFER_DELAY = 0.08; 
            let keepAliveOsc = null;
            let keepAliveInterval = null;
            let wakeLock = null;

            // NEU: Screen Wake Lock - verhindert, dass das Display (und damit der gedrosselte
            // Hintergrund-Tab) ueberhaupt erst sperrt, solange Audio an ist. Wird automatisch vom
            // Browser freigegeben, wenn der Tab den Fokus verliert - darum bei 'visibilitychange'
            // erneut anfordern, sobald die Seite wieder sichtbar wird.
            async function requestWakeLock() {
                if (!('wakeLock' in navigator)) return;
                try {
                    wakeLock = await navigator.wakeLock.request('screen');
                    console.log('[WAKELOCK] aktiv');
                } catch (e) {
                    console.log('[WAKELOCK] nicht verfuegbar:', e.message);
                }
            }
            document.addEventListener('visibilitychange', () => {
                if (isAudioOn && document.visibilityState === 'visible' && (!wakeLock || wakeLock.released)) {
                    requestWakeLock();
                }
            });

            // NEU: MediaSession - meldet dem Betriebssystem "hier laeuft echte Medienwiedergabe"
            // (wie ein Musik-Player), was Android/Chrome meist bevorzugt im Hintergrund am Leben
            // laesst statt den Tab als inaktiv einzufrieren.
            function setupMediaSession() {
                if (!('mediaSession' in navigator)) return;
                navigator.mediaSession.metadata = new MediaMetadata({
                    title: 'AE-5900 Live Audio',
                    artist: 'Funkgeraet-Fernsteuerung'
                });
                navigator.mediaSession.playbackState = 'playing';
                navigator.mediaSession.setActionHandler('play', () => { navigator.mediaSession.playbackState = 'playing'; });
                navigator.mediaSession.setActionHandler('pause', () => { navigator.mediaSession.playbackState = 'playing'; });
            }

            // NEU: Ohne staendigen Ton stufen manche Browser den Tab/Context nach einer Weile
            // Stille als "inaktiv" ein und suspendieren ihn (v.a. mobil). Ein fast lautloser
            // Dauerton (Gain ~0.0001, praktisch unhoerbar) haelt den AudioContext durchgehend
            // "beschaeftigt", damit er gar nicht erst einschlaeft - robuster als nur hinterher
            // wieder aufzuwecken.
            function startKeepAlive() {
                if (!audioContext || keepAliveOsc) return;
                const osc = audioContext.createOscillator();
                const gain = audioContext.createGain();
                gain.gain.value = 0.0001;
                osc.frequency.value = 20; // unterhalb des Hoerbereichs
                osc.connect(gain);
                gain.connect(audioContext.destination);
                osc.start();
                keepAliveOsc = osc;

                // Sicherheitsnetz: falls der Context trotzdem mal suspended wird, alle 3s aufwecken
                keepAliveInterval = setInterval(() => {
                    if (audioContext && audioContext.state === 'suspended') {
                        audioContext.resume();
                    }
                }, 3000);
            }
            function stopKeepAlive() {
                if (keepAliveOsc) { try { keepAliveOsc.stop(); } catch(e) {} keepAliveOsc = null; }
                if (keepAliveInterval) { clearInterval(keepAliveInterval); keepAliveInterval = null; }
            }

            socket.on('connect', () => {
                document.getElementById('status').innerText = "Verbunden mit Audio-Gateway";
                socket.emit('join_audio');
            });

            socket.on('audio_out', (pcmData) => {
                if (!isAudioOn || !audioContext) return;

                // NEU: Browser (v.a. mobil) suspendieren den AudioContext von selbst nach einer Weile
                // Stille (Energiesparen). resume() ist ungefaehrlich, wenn er schon laeuft - also einfach
                // vor jedem Abspielen sicherheitshalber aufwecken.
                if (audioContext.state === 'suspended') {
                    audioContext.resume();
                }
                
                const int16Array = new Int16Array(
                    pcmData instanceof ArrayBuffer ? pcmData : pcmData.buffer || pcmData
                );
                
                if (int16Array.length === 0) return;
                
                const float32Array = new Float32Array(int16Array.length);
                for (let i = 0; i < int16Array.length; i++) {
                    float32Array[i] = int16Array[i] / 32768.0;
                }

                const buffer = audioContext.createBuffer(1, float32Array.length, 16000);
                buffer.getChannelData(0).set(float32Array);
                
                const source = audioContext.createBufferSource();
                source.buffer = buffer;
                source.connect(audioContext.destination);

                const currentTime = audioContext.currentTime;
                if (nextStartTime < currentTime) {
                    nextStartTime = currentTime + BUFFER_DELAY;
                }

                source.start(nextStartTime);
                nextStartTime += buffer.duration;
            });

            function toggleAudio() {
                const btn = document.getElementById('audioBtn');
                if (!isAudioOn) {
                    // AUS VERSION 1: Feste 48000Hz Basis erzwingen, damit die Abspiel-Mathematik der 16k-Puffer exakt aufgeht!
                    audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 48000 });
                    nextStartTime = 0; 
                    isAudioOn = true;
                    btn.innerText = "AUDIO RECV: ON";
                    btn.classList.remove('off');
                    startKeepAlive();
                    requestWakeLock();
                    setupMediaSession();
                    
                    navigator.mediaDevices.getUserMedia({
                        audio: {
                            echoCancellation: false,
                            noiseSuppression: false,
                            autoGainControl: false,
                            channelCount: 1,
                            sampleRate: 48000
                        }
                    }).then(stream => {
                        document.getElementById('status').innerText = "Audio aktiv (Sende & Empfange)";
                        
                        const sourceMic = audioContext.createMediaStreamSource(stream);
                        // AUS VERSION 1: Stabiler 2048er Puffer für flüssiges 48kHz TX-Audio ohne Latenzstau
                        const processor = audioContext.createScriptProcessor(2048, 1, 1);
                        
                        sourceMic.connect(processor);
                        processor.connect(audioContext.destination);
                        
                        processor.onaudioprocess = (e) => {
                            if (!isAudioOn) return;
                            const inputData = e.inputBuffer.getChannelData(0);
                            
                            const int16Buffer = new Int16Array(inputData.length);
                            for (let i = 0; i < inputData.length; i++) {
                                let s = Math.max(-1, Math.min(1, inputData[i]));
                                int16Buffer[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                            }
                            
                            socket.emit('audio_in', int16Buffer.buffer);
                        };
                        
                        window.micStream = stream;
                        window.micProcessor = processor;

                    }).catch(err => {
                        document.getElementById('status').innerText = "Mikrofon-Fehler: " + err;
                    });

                } else {
                    isAudioOn = false;
                    btn.innerText = "AUDIO RECV: OFF";
                    btn.classList.add('off');
                    document.getElementById('status').innerText = "Audio gestoppt.";
                    stopKeepAlive();
                    if (wakeLock) { wakeLock.release(); wakeLock = null; }
                    if ('mediaSession' in navigator) { navigator.mediaSession.playbackState = 'none'; }
                    
                    if (window.micStream) {
                        window.micStream.getTracks().forEach(track => track.stop());
                    }
                    if (window.micProcessor) {
                        window.micProcessor.disconnect();
                    }
                }
            }
        </script>
    </body>
    </html>
    """)

@socketio.on('join_audio')
def on_join_audio():
    join_room('audio_room')
    print("[WEBSOCKET] Browser-Tab ist dem Audio-Raum beigetreten.")

@socketio.on('audio_in')
def handle_audio_in(pcm_data):
    """ Empfaengt native 48kHz PCM-Audio vom Browser und reicht es an Mumble weiter """
    global mumble
    if mumble and mumble.is_alive():
        if isinstance(pcm_data, str):
            return
            
        try:

            
            queue_size = mumble.sound_output.get_buffer_size() # Holt die aktuelle Puffergröße
            

            if queue_size > 5:

                return "BUFFER_THROTTLE"
                
            mumble.sound_output.add_sound(bytes(pcm_data))
        except Exception as e:
            print(f"[MIC ERROR] Fehler beim Senden an Mumble: {e}")

@socketio.on('connect')
def handle_connect():
    print("Browser-Tab hat sich mit dem Audio-Server verbunden.")
    global mumble
    if mumble is None or not mumble.is_alive():
        try:
            mumble = pymumble.Mumble(MUMBLE_HOST, BOT_NAME, port=MUMBLE_PORT)
            mumble.set_receive_sound(1) 
            mumble.start()
            mumble.is_ready()
            
            if len(mumble.channels) > 1:
                target_channel = list(mumble.channels.values())[1]
                target_channel.move_in()
                print(f"[MUMBLE] Bot in Kanal '{target_channel['name']}' verschoben.")
            else:
                print("[MUMBLE] Nur Root-Kanal vorhanden. Bleibe dort.")
                
            print("[MUMBLE] Bot erfolgreich einsatzbereit mit PCM-Decoder.")
        except Exception as e:
            print(f"[MUMBLE] Verbindung fehlgeschlagen: {e}")

def ensure_valid_cert(domain, cert_path, key_path, renew_within_days=7):
    """
    Prueft, ob ein Tailscale-Zertifikat existiert und noch ausreichend lange gueltig ist.
    Fehlt es, ist es abgelaufen oder laeuft es bald ab, wird automatisch per
    'tailscale cert <domain>' ein neues ausgestellt (dauert ein paar Sekunden).
    Prueft danach auch, ob das Skript die Dateien ueberhaupt LESEN darf - haeufige Falle,
    wenn 'tailscale cert' mal mit sudo lief und die Dateien dann root gehoeren.
    Gibt True zurueck, wenn am Ende ein gueltiges, lesbares Zertifikatspaar vorliegt.
    """
    import subprocess
    from datetime import datetime

    def read_expiry(path):
        try:
            result = subprocess.run(
                ["openssl", "x509", "-enddate", "-noout", "-in", path],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return None
            end_str = result.stdout.strip().replace("notAfter=", "")
            return datetime.strptime(end_str, "%b %d %H:%M:%S %Y %Z")
        except Exception:
            return None

    needs_renewal = True
    if os.path.exists(cert_path) and os.path.exists(key_path):
        end_date = read_expiry(cert_path)
        if end_date:
            days_left = (end_date - datetime.utcnow()).days
            if days_left > renew_within_days:
                print(f"[SSL] Zertifikat fuer '{domain}' ist gueltig bis {end_date.strftime('%d.%m.%Y')} (noch {days_left} Tage) - kein Erneuern noetig.")
                needs_renewal = False
            else:
                print(f"[SSL] Zertifikat laeuft in {days_left} Tag(en) ab ({end_date.strftime('%d.%m.%Y')}) - erneuere vorsorglich...")
        else:
            print(f"[SSL] Zertifikat fuer '{domain}' vorhanden, aber Ablaufdatum nicht lesbar - erneuere sicherheitshalber...")

    if needs_renewal:
        print(f"[SSL] Fordere neues Zertifikat fuer '{domain}' via Tailscale an - das kann ein paar Sekunden dauern...")
        try:
            result = subprocess.run(["tailscale", "cert", domain], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("[SSL] Neues Zertifikat erfolgreich ausgestellt.")
            elif "access denied" in result.stderr.lower() or "operator" in result.stderr.lower():
                # NEU: haeufigster Erststart-Fehler - tailscale cert braucht ohne gesetzten
                # Operator root-Rechte. Einmaliger Selbstheilungs-Versuch, danach nie wieder noetig.
                import getpass
                user = getpass.getuser()
                print(f"[SSL] Tailscale braucht dafuer einmalig root-Rechte. Versuche automatisch: sudo tailscale set --operator={user}")
                print("[SSL] Falls jetzt ein Passwort-Prompt im Terminal erscheint: bitte das sudo-Passwort eingeben.")
                try:
                    op_result = subprocess.run(["sudo", "tailscale", "set", f"--operator={user}"], timeout=60)
                    if op_result.returncode == 0:
                        print("[SSL] Operator gesetzt - Tailscale braucht ab jetzt nie wieder sudo. Versuche Zertifikat erneut...")
                        result = subprocess.run(["tailscale", "cert", domain], capture_output=True, text=True, timeout=30)
                        if result.returncode == 0:
                            print("[SSL] Neues Zertifikat erfolgreich ausgestellt.")
                        else:
                            print(f"[SSL WARNUNG] Immer noch fehlgeschlagen:\n{result.stderr.strip()}")
                    else:
                        print("[SSL WARNUNG] 'sudo tailscale set --operator' wurde abgebrochen oder ist fehlgeschlagen.")
                        print(f"[SSL] Bitte einmalig manuell ausfuehren: sudo tailscale set --operator={user}")
                except Exception as e:
                    print(f"[SSL WARNUNG] Konnte Operator nicht automatisch setzen ({e}).")
                    print(f"[SSL] Bitte einmalig manuell ausfuehren: sudo tailscale set --operator={user}")
            else:
                print(f"[SSL WARNUNG] 'tailscale cert' meldete einen Fehler:\n{result.stderr.strip()}")
        except FileNotFoundError:
            print("[SSL WARNUNG] Befehl 'tailscale' nicht gefunden - ist Tailscale installiert und im PATH?")
        except subprocess.TimeoutExpired:
            print("[SSL WARNUNG] 'tailscale cert' hat zu lange gebraucht (Timeout) - Netzwerkproblem?")
        except Exception as e:
            print(f"[SSL WARNUNG] Unerwarteter Fehler beim Erneuern: {e}")

    if not (os.path.exists(cert_path) and os.path.exists(key_path)):
        return False

    for p in (cert_path, key_path):
        if not os.access(p, os.R_OK):
            print(f"[SSL FEHLER] '{p}' existiert, ist fuer diesen Nutzer aber nicht lesbar (Rechteproblem).")
            print(f"              Das passiert oft, wenn 'tailscale cert' mit sudo lief. Abhilfe:")
            print(f"              sudo chown $(whoami):$(whoami) {cert_path} {key_path}")
            return False

    return True


if __name__ == '__main__':
    import os
    import subprocess

    ssl_args = {}
    cert_found = False

    try:
        ts_status = subprocess.check_output(["tailscale", "status"], text=True)
        ts_domain = None
        for line in ts_status.split('\n'):
            if ".ts.net" in line:
                for part in line.split():
                    if part.endswith(".ts.net"):
                        ts_domain = part
                        break
                if ts_domain:
                    break

        if ts_domain:
            cert_p, key_p = f"{ts_domain}.crt", f"{ts_domain}.key"
            if ensure_valid_cert(ts_domain, cert_p, key_p):
                ssl_args = {'certfile': cert_p, 'keyfile': key_p}
                cert_found = True
            else:
                # Letzter Versuch: vielleicht liegt ein gueltiges Cert im Tailscale-Systempfad
                sys_cert_p = f"/var/lib/tailscale/certs/{ts_domain}.crt"
                sys_key_p = f"/var/lib/tailscale/certs/{ts_domain}.key"
                if os.path.exists(sys_cert_p) and os.path.exists(sys_key_p) and os.access(sys_cert_p, os.R_OK) and os.access(sys_key_p, os.R_OK):
                    ssl_args = {'certfile': sys_cert_p, 'keyfile': sys_key_p}
                    cert_found = True
    except Exception:
        pass

    if not cert_found:
        # NEU: crt/key nach gemeinsamem Basisnamen zusammenfuehren statt blind crts[0]/keys[0] zu nehmen -
        # bei mehreren Zertifikatspaaren im selben Ordner (z.B. altes + neu ausgestelltes Tailscale-Cert)
        # konnten die bisher zufaellig NICHT zusammengehoeren, was genau zu diesem TLS-Handshake-Fehler
        # (SSLV3_ALERT_CERTIFICATE_UNKNOWN) fuehrt. Jetzt: nur echte Paare, davon das zuletzt geaenderte.
        local_files = os.listdir('.')
        crt_bases = {os.path.splitext(f)[0]: f for f in local_files if f.endswith('.crt')}
        key_bases = {os.path.splitext(f)[0]: f for f in local_files if f.endswith('.key')}
        matching_bases = set(crt_bases) & set(key_bases)

        if matching_bases:
            newest_base = max(matching_bases, key=lambda b: os.path.getmtime(crt_bases[b]))
            ssl_args = {'certfile': crt_bases[newest_base], 'keyfile': key_bases[newest_base]}
            cert_found = True
            if len(matching_bases) > 1:
                print(f"[SSL] Mehrere Zertifikatspaare gefunden ({', '.join(sorted(matching_bases))}), verwende das neueste: {newest_base}")
        else:
            print("[SSL WARNUNG] .crt/.key-Dateien gefunden, aber kein Paar mit gleichem Basisnamen (z.B. 'foo.crt' + 'foo.key'). Ignoriere sie.")

    if cert_found:
        print("Mumble-Audio-Gateway LAEUFT SICHER UEBER HTTPS auf Port 5001...")
    else:
        print("[WARNUNG] Keine SSL-Zertifikate gefunden! Audio laeuft ueber unsicheres HTTP (Port 5001).")

    socketio.run(app, host='0.0.0.0', port=5001, debug=False, **ssl_args)
