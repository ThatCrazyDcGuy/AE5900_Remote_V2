### Der Bluetooth-S-Meter-Teil // Geräte-Mod erforderlich

Zurück zur [README_DE](README_DE.md) · English: [BTSMETER.md](BTSMETER.md)

Ich konnte die Pinbelegung für das externe S-Meter finden.
Anstatt ein anderes Kabel/einen anderen Ausgang/Stecker zu verwenden, habe ich mich für einen ESP32-Wroom entschieden, und jetzt haben wir ein S-Meter über BT.

Sehen wir uns hier einige Fotos und Screenshots an:

![AE5900_Remote_v2](/pictures/bt-smeter.png)

![AE5900_Remote_v2](/pictures/bt-arduino.png)

![AE5900_Remote_v2](/pictures/bt-esp32device.png)

![AE5900_Remote_v2](/pictures/bt-soldering0.png)

![AE5900_Remote_v2](/pictures/bt-soldering1.png)

![AE5900_Remote_v2](/pictures/bt-soldering2.png)

Der Code ist im Ordner `ino` verfügbar.

Koppel das Gerät mit deinem Raspi/Host über `bluetoothctl` (pair, trust, connect).

Einmal ausführen (verwende hier deine eigene MAC-Adresse):

```bash
sudo rfcomm bind rfcomm0 EC:E3:34:46:D8:7E
```

```bash
echo "$USER ALL=(ALL) NOPASSWD: /usr/bin/rfcomm" | sudo tee /etc/sudoers.d/ae5900_rfcomm && sudo chmod 0440 /etc/sudoers.d/ae5900_rfcomm
```

Danach im Setup & Sync unter *S-Meter source* die Quelle "Hardware mod (ESP32)" wählen (Voreinstellung) und die MAC-Adresse bei *Bluetooth S-Meter MAC* eintragen. Mehr zu den Quellen: [SMETER_DE.md](SMETER_DE.md).

Viel Spaß!
