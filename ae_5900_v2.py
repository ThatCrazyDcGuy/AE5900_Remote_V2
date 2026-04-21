import serial
import threading
import time
import json
import os
import numpy as np
import pyaudio
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# --- PATH & CONFIG ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")
PORT = '/dev/ttyUSB0'
MODES = ["PA", "CW", "FM", "AM", "USB", "LSB"]

# Audio Setup
CHUNK = 512
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=22050, input=True, frames_per_buffer=CHUNK)

class RadioInterface:
    def __init__(self):
        self.load_config()
        self.lock = threading.Lock()
        self.is_tx = False
        self.is_rx = False
        self.is_scanning = False
        self.ptt_start_time = 0
        self.key_buffer = ""
        self.current_ch = self.config.get("last_ch", 1)
        self.mode_idx = self.config.get("last_mode", 2)
        self.scan_dir = 1 
        self.ignore_until = 0 # Sperr-Timer für Impulse (wichtig für Keypad)
        
        try:
            self.ser = serial.Serial(PORT, 115200, timeout=0.01)
            print(f"--- AE5900 Master-Emulator ONLINE (Full Feature) ---")
            threading.Thread(target=self.heartbeat_task, daemon=True).start()
            threading.Thread(target=self.listen_loop, daemon=True).start()
        except Exception as e:
            self.ser = None
            print(f"Serial Fehler: {e}")

    def load_config(self):
        default = {"ptt_timeout": 300, "last_ch": 1, "last_mode": 2, "skip_pa": False,
                   "p1_label": "NOT SET", "p2_label": "NOT SET", "p3_label": "NOT SET", "p4_label": "NOT SET"}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f: self.config = {**default, **json.load(f)}
            except: self.config = default
        else: self.config = default

    def save_config(self):
        self.config["last_ch"] = self.current_ch
        self.config["last_mode"] = self.mode_idx
        with open(CONFIG_FILE, 'w') as f: json.dump(self.config, f, indent=4)

    def heartbeat_task(self):
        """Emuliert das Mikrofon und hält die Datenverbindung aktiv"""
        while self.ser:
            try:
#                if self.ser.in_waiting == 0:
                # Nur senden, wenn wir NICHT im TX-Modus sind
                if self.ser.in_waiting == 0 and not self.is_tx:
                    with self.lock:
                        hb = bytes.fromhex("41 00 00 00 82 00 00 06")
                        self.ser.write(hb)
                        time.sleep(0.03)
                        ch_hex = self.current_ch + 15
                        status = bytes([0xAA, 0x53, 0, 0, 0, 0, 0, 0, 0, 0, ch_hex, 0, 0, 1, 0, 0, 0x06])
                        self.ser.write(status)
            except: break
            time.sleep(0.6)

    def listen_loop(self):
        """Intelligente Scan- und Signal-Erkennung mit Impuls-Filter"""
        raw_buffer = b""
        last_step_time = 0
        first_step_lock = False 
        
        while self.ser:
            if self.ser.in_waiting > 0:
                try:
                    raw_buffer += self.ser.read(self.ser.in_waiting)
                    while b'\x53' in raw_buffer:
                        idx = raw_buffer.find(b'\x53')
                        if len(raw_buffer[idx:]) < 16: break 
                        
                        # Echo-Schutz
                        if idx > 0 and raw_buffer[idx-1] == 0xAA:
                            raw_buffer = raw_buffer[idx+16:]
                            continue

                        packet = raw_buffer[idx:idx+16]
                        b1, b2 = packet[1], packet[2]
                        now = time.time()

                        # Ignoriere alles während der globalen Sperrzeit (Keypad/Sync)
                        if now < self.ignore_until:
                            raw_buffer = raw_buffer[idx+16:]
                            continue

                        # A: SIGNAL GEFUNDEN
                        if b1 > 0 or b2 > 0:
                            if not self.is_rx:
                                print(f"STATION auf CH {self.current_ch}")
                                self.is_rx = True
                                first_step_lock = True 
                                self.ser.reset_input_buffer()
                                raw_buffer = b""
                            self.is_scanning = False
                            
                        # B: SCHRITT-IMPULS
                        elif b1 == 0 and b2 == 0:
                            if self.is_rx:
                                self.is_rx = False
                                self.ser.reset_input_buffer()
                                raw_buffer = b""
                                continue

                            # 400ms Filter (0.350) // scan speed
                            if (now - last_step_time) > 0.350:
                                if first_step_lock:
                                    first_step_lock = False
                                else:
                                    self.current_ch += self.scan_dir
                                    if self.current_ch > 40: self.current_ch = 1
                                    if self.current_ch < 1: self.current_ch = 40
                                    self.save_config()
                                last_step_time = now
                                self.is_scanning = True

                        raw_buffer = raw_buffer[idx+16:]
                except: pass
            
            if self.is_scanning and (time.time() - last_step_time > 2.0):
                self.is_scanning = False
            time.sleep(0.01)

    def send_cmd(self, hex_press, hex_release):
        if not self.ser: return
        with self.lock:
            self.ser.write(bytes.fromhex(hex_press))
            time.sleep(0.08)
            self.ser.write(bytes.fromhex(hex_release))

    def super_sync(self):
        """CH 01 + ASQ OFF erzwingen"""
        self.ignore_until = time.time() + 1.2
        self.send_cmd("4100010001000006", "4100000001000006") # 0
        time.sleep(0.4)
        self.send_cmd("4100010002000006", "4100000002000006") # 1
        time.sleep(0.4)
        with self.lock:
            self.ser.write(bytes.fromhex("410001001A000006"))
            time.sleep(2.2)
            self.ser.write(bytes.fromhex("410000001A000006"))
        self.current_ch = 1; self.mode_idx = 2; self.save_config()

radio = RadioInterface()

@app.route('/')
def index(): return render_template('index.html', config=radio.config)

#@app.route('/api/audio')
#def get_audio():
#    try:
#        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
#        fft = np.abs(np.fft.rfft(data))[:32] # Die ersten 32 Frequenzbänder
#        return jsonify(fft.tolist())
#    except:
#        return jsonify([0]*32)

@app.route('/api/audio')
def get_audio():
    try:
        # Audio-Daten lesen
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
        
        # FFT berechnen
        fft = np.abs(np.fft.rfft(data))[:32]

        # 1. Rauschunterdrückung (Noise Floor)
        # Da deine Werte im 30.000er Bereich starten, setzen wir den Floor hoch
        fft = np.where(fft < 40000, 0, fft - 40000)
        
        # 2. Skalierung
        # Wir teilen durch einen hohen Wert (z.B. 5000), um die Balken zu bändigen
        # Wenn sie immer noch zu hoch sind, erhöhe die 5000 auf 8000
        fft_scaled = (fft / 36000) 
        
        return jsonify(fft_scaled.tolist())

        
        # 1. Rauschunterdrückung: Alles unter einem gewissen Wert auf 0 setzen
        noise_floor = 500  # Diesen Wert erhöhen, wenn es bei Rauschen noch zu viel zappelt
        fft = np.where(fft < noise_floor, 0, fft - noise_floor)
        
        # 2. Logarithmische Skalierung (ähnlich wie dB), damit leise und laute Töne 
        # besser ins Bild passen und nicht sofort "oben anschlagen"
        fft = np.log1p(fft) * 10 
        
        return jsonify(fft.tolist())
    except:
        return jsonify([0]*32)


@app.route('/api/cmd/<cmd>')
def api_cmd(cmd):
    key_codes = {'0':'01','1':'02','2':'03','3':'04','4':'05','5':'06','6':'07','7':'08','8':'09','9':'0A'}
    p_codes = {'P1':'1A', 'P2':'1B', 'P3':'1C', 'P4':'1D'}
    
    if cmd == 'STATUS': pass
    elif cmd == 'U': 
        radio.ignore_until = time.time() + 0.5
        radio.current_ch = (radio.current_ch % 40) + 1; radio.scan_dir = 1
        radio.send_cmd("4100010010000006", "4100000010000006")
    elif cmd == 'D': 
        radio.ignore_until = time.time() + 0.5
        radio.current_ch = 40 if radio.current_ch == 1 else radio.current_ch - 1; radio.scan_dir = -1
        radio.send_cmd("4100010011000006", "4100000011000006")
    elif cmd == 'M':
        radio.send_cmd("410001000D000006", "410000000D000006")
        radio.mode_idx = (radio.mode_idx + 1) % len(MODES)
        if radio.config.get("skip_pa") and MODES[radio.mode_idx] == "PA":
            radio.mode_idx = (radio.mode_idx + 1) % len(MODES)
    elif cmd == 'P':
        radio.is_tx = not radio.is_tx
        # PTT Code: 01 am zweiten Byte ist Press, 00 ist Release
        code = "4101000000000006" if radio.is_tx else "4100000000000006"
        
        # WICHTIG: Kein Release-Code direkt hinterher schicken!
        # Wir schicken nur den aktuellen Zustand.
        with radio.lock:
            radio.ser.write(bytes.fromhex(code))
        
        radio.ptt_start_time = time.time()
        # Sperre die Status-Interpretation für 500ms, damit das Gerät umschalten kann
        radio.ignore_until = time.time() + 0.5

#    elif cmd == 'P':
#        radio.is_tx = not radio.is_tx
#        code = "4101000000000006" if radio.is_tx else "4100000000000006"
##        radio.ignore_until = time.time() + 0.5
#        radio.send_cmd(code, code); radio.ptt_start_time = time.time(); radio.ignore_until = time.time() + 0.50 if radio.is_tx else 0
##        radio.ignore_until = time.time() + 0.50
    elif cmd == 'S': radio.super_sync()
    elif cmd.startswith('K'):
        digit = cmd[1:]
        if digit in key_codes:
            radio.send_cmd(f"41000100{key_codes[digit]}000006", f"41000000{key_codes[digit]}000006")
            radio.key_buffer += digit
            if len(radio.key_buffer) == 2:
                radio.ignore_until = time.time() + 0.8
                try:
                    val = int(radio.key_buffer)
                    if 1 <= val <= 40: radio.current_ch = val
                except: pass
                radio.key_buffer = ""
    elif cmd in p_codes: radio.send_cmd(f"41000100{p_codes[cmd]}000006", f"41000000{p_codes[cmd]}000006")
    elif cmd.startswith('SET_'):
        parts = cmd.split('_'); val = request.args.get('val')
        if "SKIP" in cmd: radio.config["skip_pa"] = (val.lower() == 'true')
        else: radio.config[f"{parts[1].lower()}_label"] = val
    elif cmd.startswith('T'):
        try: radio.config["ptt_timeout"] = int(cmd[1:])
        except: pass

    if radio.is_tx and (time.time() - radio.ptt_start_time >= radio.config["ptt_timeout"]):
        radio.is_tx = False; radio.send_cmd("4100000000000006", "4100000000000006")

    radio.save_config()
    rem = int(radio.config["ptt_timeout"] - (time.time() - radio.ptt_start_time)) if radio.is_tx else radio.config["ptt_timeout"]
    return jsonify({
        "CH": str(radio.current_ch).zfill(2), "MODE": MODES[radio.mode_idx], 
        "PTT": "ON" if radio.is_tx else "OFF", "REMAINING": max(0, rem), 
        "BUSY": radio.is_rx, "SCAN": radio.is_scanning
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
