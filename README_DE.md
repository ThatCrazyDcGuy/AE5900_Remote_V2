# AE5900 Remote Control V2

Switch lang. to EN: [🇬🇧 English](https://github.com/ThatCrazyDcGuy/AE5900_Remote_V2/blob/main/README.md)

## DEUTSCHE VERSION DER README:

Ein LAN/Web Remote Rig Control System für das Albrecht AE-5900 Funkgerät, das das AMM-500 Mikrofon simuliert. Das AE5900 wird so per Webbrowser in einem Webinterface bedienbar.

### Das Vorwort:

**WARNUNG!!!** Es besteht die Gefahr, dass die Nutzung je nach Landesbestimmung strafbar ist.
Klärt das mit eurem Gewissen. Ich bin nicht eure Mutti! Aber hier trotzdem einige Details:

#### Sicherheit

Eine solche Oberfläche darf unter keinen Umständen direkt aus dem Internet erreichbar sein. Nutze sie im eigenen Netzwerk oder über ein VPN, zum Beispiel Tailscale.

Die Weboberfläche ist mit einem Passwort geschützt. Nach dem Update (oder einer Neuinstallation) fordert die Seite beim ersten Besuch dazu auf, eines zu setzen. Auch der Installer kann danach fragen (`bash install.sh --with-password`). Vergessen? Auf dem Raspberry Pi: `python3 ae_auth.py --set-password`. Das Passwort schützt die Weboberfläche (Ports 5000 und 5443), **nicht** die übrigen Ports in der Tabelle.

Diese Ports dürfen niemals nach außen erreichbar sein:

| Port | Was es ist | Schutz |
|---|---|---|
| 5000/TCP | Weboberfläche (HTTP) | Passwort |
| 5443/TCP | Weboberfläche (HTTPS, Handy-Mikrofon), nur mit Tailscale | Passwort |
| 4532/TCP | Hamlib/rigctl-Proxy für fldigi, OpenWebRX, JS8Call, WSJT-X, ... Wer ihn erreicht, kann Kanal und Modus ändern und den Sender tasten. | **nicht möglich** (das rigctl-Protokoll kennt keine Anmeldung) |
| 2442/UDP | Digimode-Gateway: Statuspakete von JS8Call/WSJT-X schalten PTT. Ein gefälschtes Paket tastet den Sender. | **nicht möglich** |
| 4533/TCP | internes rigctld, lauscht nur auf 127.0.0.1 | von außen nicht erreichbar |
| 64738/TCP+UDP | Mumble-Server, nur wenn installiert (`--with-mumble`) | eigene Mumble-Einstellungen |
| 22/TCP | SSH (der Installer installiert `openssh-server`; gehört nicht zu diesem Projekt) | dein SSH-Setup, am besten nur mit Schlüsseln |

Gib keinen dieser Ports im Router frei und nutze für den Raspberry Pi weder Portweiterleitung noch DMZ oder UPnP.

Programme auf **anderen** Rechnern, die PTT über die Weboberfläche schalten (der PTT-Knopf in OpenWebRX, JS8Call mit `curl`), brauchen den Schlüssel, den du in Setup & Sync unter „Security" findest. Er erlaubt nur PTT, sonst nichts. Programme auf dem Raspberry Pi selbst (127.0.0.1) brauchen keinen Schlüssel.

#### Rechtliches

Als lizenzierter Funkamateur darfst du je nach regionalen Vorschriften möglicherweise eine Fernsteuerung nutzen.

Für nicht lizenzierte Funker, etwa im CB-Funk, ist eine „unbeaufsichtigte" (unbemannte) Funkstelle in der Regel nicht erlaubt. Betreibst du das System jedoch in deinem eigenen privaten Netzwerk, in unmittelbarer Nähe des Funkgeräts, sodass du es bei einer Störung jederzeit von Strom oder Netzwerk trennen könntest, und bleibst du auf deinem eigenen Grundstück, wird das normalerweise nicht als rechtliches Problem angesehen.

Die Regeln unterscheiden sich von Land zu Land. Das ist keine Rechtsberatung; informiere dich über die für dich geltenden Vorschriften.

### Schnellstart in fünf Schritten

1. Das Zusatzgerät bauen (Teileliste und Bilder weiter unten) und zwischen Raspberry Pi und Mikrofonbuchse des AE5900 hängen.
2. Auf dem Raspberry Pi diese Zeilen in die Konsole kopieren:

```bash
git clone https://github.com/ThatCrazyDcGuy/AE5900_Remote_V2
cd ~/AE5900_Remote_V2/
bash install.sh
reboot
```

Der Installer hat einige Optionen, siehe `bash install.sh --help`:

- `--with-sdr`: richtet zusätzlich einen RTL-SDR-Dongle als S-Meter ein
- `--with-password`: fragt schon bei der Installation nach dem Web-Passwort (sonst fragt die Seite beim ersten Besuch)
- `--with-mumble`: installiert zusätzlich Mumble (optional, WebAudio braucht es nicht)
- `--no-tailscale`: ohne Tailscale (dann nur HTTP auf Port 5000, kein HTTPS)
- `--no-service`: ohne Autostart-Dienst

Während der Installation zeigt Tailscale einen Anmelde-Link. Diesen im Browser öffnen und der Anleitung folgen. Der Installer lässt sich jederzeit erneut starten und ergänzt nur, was fehlt. Sein Log liegt unter `~/ae5900-install.log`.

3. Im Browser `http://IP-DES-RASPBERRY:5000` öffnen (oder `https://IP-DES-RASPBERRY:5443`, wenn auch gesendet werden soll). Beim ersten Besuch fordert die Seite dazu auf, ein Passwort zu setzen (einmal pro Gerät, mit dem du dich anmeldest).
4. Ganz unten auf "SETUP & SYNC" tippen und den Sync ausführen.
5. Die Labels der Tasten P1 bis P4 so eintragen, wie sie am AE5900 eingestellt sind (Mic Type 2).

Aktualisieren später immer mit `git pull` und das Programm neu starten. Eigene Einstellungen und das eigene Hintergrundbild bleiben dabei erhalten.

> **Wichtig:** Das AE5900 immer nur von **einem Gerät gleichzeitig** über die Weboberfläche bedienen. Hamlib/Rigctl-Programme (z. B. OpenWebRX, fldigi) neben einem Browser sind in Ordnung. Mehrere Browser oder Handys gleichzeitig sind es nicht, weil dann der PTT-Killswitch bei Verbindungsverlust nicht mehr zuverlässig greift.

### Hauptziel des Projekts:

Entwicklung einer LAN/Web-Fernsteuerung für das Albrecht AE-5900.
Sinn und Zweck ist schlussendlich auch, das Thema Funk wieder zu beleben und attraktiver zu machen.
Flexible Lösungen verschaffen besseren Zugang. Und genau das soll dieses Projekt ermöglichen.

### Ein Bild erzählt dir mehr als deine Ehefrau:

- Ein Screenshot vom aktuellen UI, im Browser, auf dem Smartphone

![AE5900_Remote_v2](/pictures/webui_last.jpg)

1. Visuelles Audiofeedback (Balken, Wasserfall oder beides)
2. Lautstärke des Mikrofons regelbar
3. Optimierte Scan-Funktion mit regelbarer Geschwindigkeit
4. Clarifier
5. Lock
6. Mute
7. Vox
8. MW (Multi-Channel-Scan)
9. Squelch // Autosquelch
10. Der PTT-Kill-Schalter wird 30 Sekunden nach Verbindungsverlust aktiviert.
11. Eigene Rogerbeeps erstellen. Einfach zu den Bestätigungstönen im Ordner beeps hinzufügen.
12. Physische PTT-Taste/Sondertaste am Telefon oder an der Tastatur verwenden.
13. Ländercodes müssen im WebUI und am Gerät eingestellt werden.
14. Hamlib/Rigctl kompatibel (flrig, fldigi, rigctl, grig, openwebrx, js8call & wsjt-cb).
15. S-Meter aus einem RTL-SDR-Dongle oder vom eigenen OpenWebRX-Server
16. Wer sich traut, das Gerät zu öffnen und zu löten: externes S-METER per Bluetooth (ESP32).
17. Web-Audio HTTP nur RX / HTTPS RX und TX
18. Hintergrundbild für einen individuellen Stil ändern (einfach nur zum Spaß)

Hier werden verschiedene Funktionen demonstriert. Rigctl und Hamlib sowie ein Bluetooth-S-Meter sind implementiert.

[![AE5900 Webinterface V2 ](https://img.youtube.com/vi/0-UP0ARVENU/0.jpg)](https://www.youtube.com/watch?v=0-UP0ARVENU)

- Ein Foto vom neusten Prototyp ohne Klinkenstecker. Audio und Steuerung über RJ45.

![AE5900_Remote_v2](/pictures/v218mar2.jpeg)

### Mindestanforderung für dieses Projekt:

1. Die Fähigkeit zu lesen
2. Die Fähigkeit zu verstehen
3. Die Fähigkeit umzusetzen
4. Lötkolbenerfahrung
5. Raspberry Pi 3
6. Etwas Kleingeld für die Teile

### Die Hardware-Bastelei

Mit Bildern und allem, was man wissen muss.

- Vorab die Komponenten für den Audiofilter und was man so zum Basteln nutzen kann. Das meiste davon hatte ich in meiner Bastelkiste.

Für die Audiofilter nutzen wir hier nun:

1. 1x 600:600 Ohm Transformator
2. 1x 100 Ohm Widerstand
3. 1x 10 kOhm Widerstand
4. 1x Keramikkondensator 10nF (103) (mindestens einer, um die HF zu filtern)
5. 1x Elko 10µF (ca. 16 - 50 V)

Restliche Komponenten:

1. USB-Breakoutboard oder einen Hub
2. FT232RL FT232 FTDI USB 3,3 V / 5,5 V zu TTL Seriell Adapter
3. USB-Soundkarte
4. RJ45-Terminal
5. Ein Gehäuse aus Metall

![AE5900_Remote_v2](/pictures/allpartsv2.jpg)

- Ich habe euch ein schönes Bild gemalt. Sieht zwar aus wie von einem Dreijährigen, aber so versteht's vielleicht jeder Hobbybastler und Lötkolbenbesitzer.

![AE5900_Remote_v2](/pictures/overview_v3.png)

Man kann die USB-Geräte natürlich auch einfach in einen USB-Hub stecken, aber wo bleibt da der Spaß am "so klein wie möglich" bauen?
Die beiden Filter muss man aber dennoch löten.

#### Wie ist das eigentlich möglich?

Das AMM-500 sendet seriell HEX-Codes an das AE-5900 und das AE-5900 antwortet entsprechend. Damit ist so einiges möglich.
Um die Bastelei zu verwirklichen, musste ich zwischen den beiden Geräten mitlesen.
Prinzip: Man in the middle.

Da das AE-5900 selbst erst nach einem Handshake mit dem AMM-500 seine Codes freigibt, musste dieses erst gekauft und sehnlichst erwartet werden.

#### Benötigte Software // Installation

Mit dem Block im Schnellstart wird der Raspberry Pi zuerst mit dem Script und den System-Updates gefüttert.
Danach wird alles Notwendige wie Python, Audio, Tailscale (und auf Wunsch Mumble) installiert.

Wer Tailscale nutzen möchte: Den erzeugten Tailscale-Link in den Browser kopieren und der Anleitung folgen, dann neu starten.

### So funktioniert es:

1. Schließe das gebastelte Gerät an einen Raspberry Pi oder einen anderen Host-Rechner an, auf dem das Python-Skript ausgeführt werden kann. Dieses Gerät dient dann als Server.
2. Adapter mit dem Mikrofonport verbinden.
3. Um den Lautsprecher stummzuschalten, muss ein Klinkenstecker als Blindstecker in den PA/EXT-Ausgang eingesteckt werden.
4. Stelle die Ausgabelautstärke des AE5900 von 0 auf etwa 75 % am Lautstärkeregler hoch.
5. Sorge für eine ordnungsgemäße Erdung, um HF-Störungen zu vermeiden.
6. Bestenfalls ist das AE5900 bereits auf FM und den Kanal 1 gesetzt.
7. Stelle an deinem AE5900 Mikrofon TYPE 2 ein und setze deine P1 - P4 Key-Shortcuts.
8. Führe `python3 ae_5900_v2.py` auf dem Hostrechner/Server aus (der Installer startet es beim Booten bereits automatisch).
9. Öffne auf dem Endgerät `http://HOSTNAMEIP:5000` oder `https://HOSTNAMEIP:5443` in deinem Browser. Beim ersten Besuch setzt du ein Passwort. Danach solltest du bereits Kontrolle über dein AE5900 haben.
10. Öffne ganz unten im WebUI das Setup und führe den Sync aus.
11. Setze die entsprechenden Labels für die P1 bis P4 Tasten so, wie du sie am AE5900 gesetzt hast.
12. Auf dem Hostrechner solltest du im Lautstärkeregler (pavucontrol) gegebenenfalls Anpassungen machen. Typische Anpassung: Menüpunkt "Konfiguration", Standard-Soundkarte deine im Netzwerk angebundene Soundkarte.

Das Script ist für alle Regionen inkl. VFO-Mode ausgelegt.

Das ist eigentlich alles, und wer nicht komplett ahnungslos ist, bekommt das schon hin.

### Audio Setup, besonders für jene, die Mumble anstatt WebAudio nutzen möchten:

[Audio-Setup (AUDIOSETUP_DE.md)](AUDIOSETUP_DE.md)

### HAMLIB / OpenWebRX Steuerungs-Setup:

[Hamlib / Rigctl / OpenWebRX (HAMLIBOWRX_DE.md)](HAMLIBOWRX_DE.md)

### S-Meter (drei Quellen):

Die Quelle wird im "Setup & Sync" unter "S-Meter source" gewählt: ESP32-Hardware-Mod, RTL-SDR-Dongle oder der eigene OpenWebRX-Server.

[S-Meter einrichten (SMETER_DE.md)](SMETER_DE.md)

### Bluetooth-S-Meter Lötanleitung und Setup:

[Bluetooth-S-Meter (BTSMETER_DE.md)](BTSMETER_DE.md)

### Es empfiehlt sich, zu Hause einen WebSDR zu betreiben, um die Installation ggf. zu überprüfen (Kanal/Modulation).
Ein guter WebSDR lässt sich einfach mit OpenWebRX, einem Raspberry Pi, einem RTL-SDR-Dongle (z. B. RTL-SDR Blog V3 oder V4 / Nooelec NESDR V5) und einer Antenne aufbauen.

### Fehlersuche

- **Kein Sendeton?** Prüfe die Mikrofonverstärkung am AE5900 selbst. "MIC +/-" im Webinterface regelt nur die Soundkarte. Die Mikrofonverstärkung am Gerät darf nicht auf 0 stehen. Zum Senden mit dem Handy-Mikrofon wird HTTPS (Port 5443) benötigt.
- **Läuft das Programm?** `systemctl --user status ae5900`
- **Log lesen:** `sudo journalctl _SYSTEMD_USER_UNIT=ae5900.service -f` (ohne `sudo` bleibt `journalctl --user` auf dem Raspberry Pi OS leer)
- **Neu starten:** `systemctl --user restart ae5900`
- **`git pull` verweigert das Update ("lokale Änderungen" an `install.sh`)?** Einmal `git config core.fileMode false` ausführen (ein früheres `chmod +x` hat die Dateirechte geändert), dann `git pull` erneut. Wenn es weiter meckert: `git checkout -- install.sh`. Eigene Einstellungen (`config.json`) und Hintergrundbild bleiben unberührt.
- **Probleme bei der Installation:** Das Log liegt unter `~/ae5900-install.log`.
- **Hilfe holen:** Bitte im Telegram-Kanal schreiben (siehe Kontakt / Feedback unten): was du gemacht hast, die passenden Logzeilen (z. B. `[AUDIO-ROUTING] Karte: ...`), deine Soundkarte (`pactl list short sources`) sowie Browser und Version.

### Was noch fehlt // Was noch nicht funktioniert

1. Es fehlt immer irgendetwas. Was nicht da ist, das kommt noch.

### Versionsinformationen & Änderungsübersicht

Aktuell: **V-231026 PWD**. Aktualisieren immer mit `git pull`.

1. Sicherheit: Die Weboberfläche ist jetzt mit einem Passwort geschützt. Nach dem Update fordert die Seite beim ersten Besuch dazu auf, eines zu setzen (nur aus dem eigenen Netz möglich: LAN, Tailscale oder der Raspberry Pi selbst). Bis zur Anmeldung liegt ein halbtransparentes Fenster über der Oberfläche. Das Passwort wird nur als Hash in der `config.json` gespeichert (neue Einträge `auth_hash`, `auth_secret`, `api_key`), die Anmeldung gilt pro Gerät 30 Tage, falsche Passwörter werden gebremst (5 Versuche, dann 30 s, 60 s, 120 s ... bis zu 15 Minuten je Adresse). Setup & Sync hat einen neuen Block „Security": Passwort ändern (meldet alle anderen Geräte ab), Abmelden und der Schlüssel für andere Programme. Der Installer kann ebenfalls danach fragen (`bash install.sh --with-password`, oder die Frage am Ende beantworten). Vergessen: auf dem Raspberry Pi `python3 ae_auth.py --set-password` (vorher das Programm stoppen: `systemctl --user stop ae5900`).
2. Was geschützt ist: alles außer der Seite selbst, also alle `/api/...`-Aufrufe, der WebSocket (Audio, Mikrofon, Wasserfall) und die Kamera. Die Kameraseite `/cam` und der Pop-out-Link funktionieren, nachdem du dich auf dem jeweiligen Gerät angemeldet hast. Anfragen, die eine Webseite von einer anderen Seite in deinem Browser schickt, werden immer abgewiesen (das schließt den Weg für „Drive-by"-Angriffe aus dem Internet beim Surfen, auch ohne Passwort). Die Terminal-Befehle der Custom-Tasten werden nicht mehr an Unangemeldete ausgeliefert und lassen sich nur nach der Anmeldung ändern.
3. Programme auf **anderen** Rechnern: Die PTT-Aufrufe (`/api/rig/ptt/0|1` und `/api/cmd/TX?state=...`) brauchen jetzt einen Schlüssel, weil sie sich nicht anmelden können: `?key=SCHLÜSSEL` (bzw. `&key=SCHLÜSSEL`) anhängen oder als Header `X-API-Key` senden. Den Schlüssel findest du in Setup & Sync -> Security (SHOW). Er erlaubt nur PTT, sonst nichts. Programme auf dem Raspberry Pi selbst (127.0.0.1), zum Beispiel `curl` aus JS8Call auf dem Pi, arbeiten wie bisher ohne Schlüssel. Der OpenWebRX-PTT-Knopf im Hamlib/OpenWebRX-Handbuch hat jetzt eine Zeile `ALBRECHT_KEY` für den Schlüssel.
4. Nicht geschützt, weil diese Protokolle keine Anmeldung kennen: der Hamlib/rigctl-Port 4532 und der Digimode-UDP-Port 2442. Niemals aus dem Internet erreichbar machen. Die README listet jetzt alle Ports und ihren Zweck.
5. Das Geheimnis, mit dem die Anmeldung signiert wird (ersetzt das feste Wort im Programm), wird auf jeder Installation einzeln erzeugt. Die `config.json` ist nur noch für den Besitzer lesbar.

Die vollständige Historie steht in der [Änderungsübersicht](CHANGELOG_DE.md).

### Extras und Testläufe

1. JS8Call funktioniert damit recht gut. Man muss natürlich etwas an den Settings rumspielen und VOX aktivieren.
Es sollte allerdings eine Kleinigkeit sein, hier noch eine PTT-Funktion für entsprechende Software zu bauen.

2. User-Feedback vom 30. April 2026: Linux Mint um die Version 21.3 und darunter versteht die Python-Vol- und Vol+ nicht.
Nur falls jemand auf so einem System testet. Ein Mint-Upgrade hilft, das Problem zu lösen.

### Was du sonst noch erwarten kannst:

Nichts weiter als meine Erfahrung.
Ich werde keinen persönlichen Support anbieten.
Aber ich werde einige Skripte, Bilder und Ideen hochladen, um sie mit anderen zu teilen.

Ich bin kein Programmierer, aber ich kann Texte lesen, verstehen, umsetzen und in meine Projekte einbauen.

Ich übernehme keine Verantwortung für eure Basteleien. Bei meinem lieben Betatester und bei mir funktionieren Software wie Hardware einwandfrei.
Das Audio bekam in QSOs durchweg gutes Feedback.

### Danke, Leute:

Ein besonderer Dank geht an alle verweisenden Seiten, die ich in letzter Zeit entdeckt habe:

- [blog.adafruit.com](https://blog.adafruit.com/2026/06/28/a-remote-web-rig-control-system-for-the-albrecht-ae-5900-radio-hamsunday/)
- [korben.info](https://korben.info/il-a-transforme-sa-radio-cb-en-station-pilotable-depuis-un-navigateur-web.html)
- [hackaday.com](https://hackaday.com/2026/06/03/web-based-control-for-a-cb-radio/)
- [daily.dev](https://daily.dev/posts/web-based-control-for-a-cb-radio-hvgarjfyn)
- [radiowalkietalkie.com](https://www.radiowalkietalkie.com/news/cb-radio-web-remote-control-solution-85555228.html)
- [bingo01](https://bingo01.de/)
- [simonthewizard.com](https://simonthewizard.com/)

Wo die Leute darüber sprechen:

- [cb-lounge.de](https://forum.cb-lounge.de/)
- [funkbasis.de](https://www.funkbasis.de/)
- [cbfunk.ch](https://cbfunk.ch/)
- [cbfunker.online](https://cbfunker.online/)
- [worldwidedx.com](https://www.worldwidedx.com/threads/web-control-of-cb-radio.271268/#post-872377)

### Kontakt / Feedback

Neuigkeiten, Updates und dein Feedback: [t.me/gz62cb](https://t.me/gz62cb)
