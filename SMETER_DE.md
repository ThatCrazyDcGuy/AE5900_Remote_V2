### S-Meter: Quelle wählen

Zurück zur [README_DE](README_DE.md) · English: [SMETER.md](SMETER.md)

Das S-Meter des AE-5900 zeigt sich nur am Gerät. Für das Webinterface gibt es drei Quellen. Wähle eine unter **Setup & Sync → S-Meter source**:

| Quelle | Was du brauchst | Hinweis |
|---|---|---|
| Hardware mod (ESP32) | Geöffnetes Gerät, ESP32 | Bluetooth, siehe [BTSMETER_DE.md](BTSMETER_DE.md). Das ist die Voreinstellung. |
| SDR dongle (RTL-SDR) | RTL-SDR-Dongle mit eigener Antenne, Paket `rtl-sdr` | Misst die Leistung auf dem aktuellen Kanal. |
| OpenWebRX (local) | Dein eigener, nicht öffentlicher OpenWebRX-Server | Liest den S-Meter-Wert eines zusätzlichen OpenWebRX-Clients. |
| Off | - | Kein S-Meter. |

Beim Senden zeigt das S-Meter 0 (das gilt auch für den ESP32-Mod).

#### Kalibrierung (SDR und OpenWebRX)

Jede Quelle meldet einen Pegel in dB. Du legst fest, welcher Wert 0 % und welcher 100 % sein soll:

1. **Floor (0 %)**: Auf einen ruhigen Kanal gehen und neben *Floor* auf **= now** drücken.
2. **Full (100 %)**: Wenn eine starke Station auf dem Kanal ist, neben *Full* auf **= now** drücken.
3. **Smoothing**: Kleine Werte ergeben einen ruhigen Zeiger, 1 schaltet die Glättung aus.

Die Statuszeile darunter zeigt den aktuellen dB-Wert. Voreinstellungen: SDR -60 dB / -20 dB, OpenWebRX -85 dB / -30 dB. Jede Installation ist anders, du wirst also nachstellen müssen.

#### RTL-SDR-Dongle verwenden

Am einfachsten geht es mit dem Installer: `bash install.sh --with-sdr` installiert die Werkzeuge, sperrt den DVB-Treiber und prüft den Dongle. Von Hand:

```bash
sudo apt install rtl-sdr
```

- Nimm einen Dongle (am besten mit eigener Antenne), den **nichts anderes** gleichzeitig nutzt, zum Beispiel nicht dein OpenWebRX.
- Wird der Dongle nicht gefunden, hat evtl. der DVB-Treiber ihn belegt. Einmal auf die Sperrliste setzen und neu starten:

```bash
echo "blacklist dvb_usb_rtl28xxu" | sudo tee /etc/modprobe.d/blacklist-rtl.conf
```

- *SDR gain* ist eine Zahl in dB oder `auto`. Starte mit 30 und stelle nach.

#### OpenWebRX als S-Meter verwenden

- Nutze deinen **eigenen, nicht öffentlichen** OpenWebRX-Server (keinen öffentlichen). Das Programm verbindet sich als zusätzlicher Client und folgt Kanal und Modus des Funkgeräts.
- Trage die Adresse unter *OpenWebRX address* ein (Voreinstellung `127.0.0.1:8073`).
- OpenWebRX muss dafür nicht gestoppt werden.
- Auf diesem Server sollte immer nur eine Person gleichzeitig arbeiten.
