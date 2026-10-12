### Der Bluetooth-S-Meter-Teil // Geräte-Mod erforderlich

Ich konnte die Pinbelegung für das externe S-Meter finden.
Anstatt ein anderes Kabel/einen anderen Ausgang/Stecker zu verwenden, habe ich mich für die Verwendung eines ESP32-Wrooms entschieden und jetzt haben wir ein S-Meter über BT.

Sehen wir uns hier einige Fotos und Screenshots an:

![AE5900_Remote_v2](/pictures/bt-smeter.png)

![AE5900_Remote_v2](/pictures/bt-arduino.png)

![AE5900_Remote_v2](/pictures/bt-esp32device.png)

![AE5900_Remote_v2](/pictures/bt-soldering0.png)

![AE5900_Remote_v2](/pictures/bt-soldering1.png)

![AE5900_Remote_v2](/pictures/bt-soldering2.png)

Code ist im Ino-Ordner verfügbar.

Kopple das Gerät mit deinem Raspi/Host über Bluetoothctl / Pair / Trust / Connect

Einmal ausführen:

sudo rfcomm bind rfcomm0 EC:E3:34:46:D8:7E <- Verwende hier deine eigenen Mac

echo „$USER ALL=(ALL) NOPASSWD: /usr/bin/rfcomm“ | sudo tee /etc/sudoers.d/ae5900_rfcomm && sudo chmod 0440 /etc/sudoers.d/ae5900_rfcomm

Viel Spaß!
