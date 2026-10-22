# Änderungsübersicht

English: [CHANGELOG.md](CHANGELOG.md) · Zurück zur [README_DE](README_DE.md)

Aktualisieren immer mit `git pull`, danach das Programm neu starten.

Hinweis: Einige Versionsbezeichnungen in älteren Einträgen wurden korrigiert (der Datumsteil ist TTMMJJ).

### V-221026 TLS (aktuell)

1. Fehlerbehebung: HTTPS (Port 5443) stirbt nach einem Netzwechsel, einem Verbindungsabbruch oder einem Tailscale-Neuladen am Handy nicht mehr. Ursache: Der Webserver machte den TLS-Handshake in der Schleife, die Verbindungen annimmt. Eine einzige halbfertige Verbindung blockierte damit jede weitere HTTPS-Verbindung (reines HTTP lief weiter, nur ein Neustart half). Jetzt macht jede Verbindung ihren Handshake im eigenen Thread mit 10 s Zeitlimit, tote Verbindungen räumt TCP-Keepalive auf. Mit einem Testaufbau nachgestellt und geprüft (hängende, kaputte und halb geöffnete Verbindungen). Der echte WebSocket-/Mikrofon-Teil über HTTPS muss noch auf einem echten Gerät geprüft werden.
2. Mikrofon-Absicherung: Fällt das Mikrofon bei aktivem „Talk (mic)" weg (eingehender Anruf, anderes Programm belegt das Mikrofon, Berechtigung entzogen), schaltet der Browser das Mikrofon jetzt aus und gibt PTT frei, statt ohne Modulation weiterzusenden. Der Knopf zeigt dann „Mic lost (call?)".

### V-211026 UIS

1. Anzeige-Einstellungen werden jetzt in der `config.json` gespeichert und gelten auf allen Geräten, sobald man sie einmal ändert: der Display-Modus (Bars / Waterfall / Both / RF waterfall), Kontrast und Tempo des Audio-Wasserfalls und der Kontrast des HF-Wasserfalls. Solange das Programm noch keinen Wert gespeichert hat, gilt weiterhin der Wert, den sich der Browser gemerkt hatte, es geht also nichts verloren. Die S-Meter-Quelle und die Schalter des HF-Wasserfalls lagen schon in der `config.json`. Audio-Einstellungen und Tastenkürzel bleiben bewusst pro Gerät.

### V-211026 OWF

1. HF-Wasserfall mit OpenWebRX als S-Meter-Quelle: Das Programm übernimmt die Wasserfall-Zeilen jetzt auch aus deinem OpenWebRX (Spektrum des ganzen Profils, auf das Fenster um den Kanal zugeschnitten). So geht es ohne eigenen Dongle, z. B. wenn OpenWebRX den Dongle schon belegt. Anzeige-Modus „RF waterfall" und Einstellungen (Breite, Kontrast) sind dieselben wie beim Dongle. Eigene Sendungen werden immer angezeigt (rot markiert), weil OpenWebRX nur mithört. Die Auflösung hängt vom OpenWebRX-Profil ab (Abtastrate / FFT-Größe) und kann gröber sein als beim eigenen Dongle. Noch nicht gegen ein echtes OpenWebRX getestet.

### V-211026 RFF

1. RF-Wasserfall-Anzeige: Die grüne Linie auf dem aktuellen Kanal entfällt (sie verdeckte das Signal). Das Dreieck oben markiert die Mitte, die Kanalnummer und die grauen Nachbarlinien bleiben.

### V-211026 RFE

1. Fehlerbehebung: Im Display-Modus „RF waterfall" scrollt der Wasserfall jetzt auf dieselbe Weise wie der normale Wasserfall (die neuen Zeilen blieben auf manchen Geräten nicht sichtbar). Das Dreieck oben (Fenstermitte = aktueller Kanal) wird wie bei „Both" wieder angezeigt.

### V-211026 RFD

1. Der HF-Wasserfall ist jetzt ein vierter ANZEIGE-MODUS (SETUP & SYNC -> Display mode -> „RF waterfall (SDR dongle)"). Er füllt das gesamte Display von Rand zu Rand, das Kanalraster ist markiert (aktueller Kanal grün, Nummer über dem S-Meter-Balken). Eigene Sendungen erscheinen bei eingeschaltetem „keep running while transmitting" rot am linken Rand. Die Wahl wird je Browser gemerkt. Das Auswählen schaltet den Wasserfall im Programm ein (gerechnet wird weiterhin nur, solange ein Browser zuschaut). Nötig ist die S-Meter-Quelle „SDR dongle", sonst weist das Display darauf hin. Breite und Kontrast stellst du im SDR-Bereich ein.

### V-211026 WFL

1. HF-Wasserfall (optional, standardmäßig aus) in SETUP & SYNC: Mit der S-Meter-Quelle „SDR dongle" zeigt eine zweite Anzeige das Funkspektrum um den aktuellen Kanal, sodass man QSOs auf den Nachbarkanälen sieht. Das Fenster (40 / 60 / 100 / 200 kHz breit) liegt mittig auf dem Kanal. Das Kanalraster ist markiert, der aktuelle Kanal grün. Die Farben folgen dem Rauschteppich automatisch, „Contrast" stellt den Bereich ein. Genutzt werden die IQ-Daten, die das S-Meter ohnehin vom Dongle liest. Bei ausgeschaltetem oder nicht geöffnetem Wasserfall wird nichts gerechnet und nichts gesendet. Während er offen ist, braucht er grob 10-15 % eines Raspberry-Pi-3-Kerns (Schätzung, nicht gemessen).
2. Optional „keep running while transmitting": Der Dongle wird beim Senden nicht freigegeben, dein eigenes Signal erscheint im Wasserfall (rot am linken Rand markiert). Nur mit einer eigenen Empfangsantenne in einigem Abstand. Den Dongle niemals an die Sendeantenne oder den Antennenanschluss des Funkgeräts hängen. Der S-Meter-Wert wird beim Senden nicht aktualisiert.

### V-201026 CAM

1. Kamera in SETUP & SYNC (optional, standardmäßig aus): Das AE5900 lässt sich mit einer USB-Webcam beobachten. Ein Dropdown listet die gefundenen Kameras, dazu Auflösung (320x240 / 640x480 / 1280x720), horizontal spiegeln und vertikal spiegeln. VORSCHAU zeigt das Bild an Ort und Stelle, `/cam` zeigt nur das Bild (für einen zweiten Bildschirm oder als Lesezeichen). Es braucht kein OpenCV, nur das Paket `ffmpeg` (`sudo apt install ffmpeg` oder `bash install.sh --with-cam`). ffmpeg läuft nur, solange jemand zuschaut. Eine ausgeschaltete Kamera verursacht daher weder Last noch Netzwerkverkehr. Die Kamera muss MJPEG liefern (praktisch jede USB-Webcam tut das).
2. Startprüfung: Fehlt ein benötigtes Python-Paket, zeigt das Programm jetzt die genaue Zeile `sudo apt install ...` statt eines Tracebacks. Optionale Programme (ffmpeg, rigctld, rtl_sdr) werden beim Start nur gemeldet, wenn die zugehörige Funktion eingeschaltet ist.

### V-181026 LSC

1. Smartphone-Querformat: Im Querformat gibt es drei Spalten. Links das Zahlenfeld mit CLAR +/STEP/CLAR - über MIC +/RB/MIC -, in der Mitte Display und Funktionstasten, rechts PTT und die beiden Audio-Tasten. SETUP & SYNC bleibt darunter. Hochformat und Desktop-Ansicht bleiben unverändert.

### V-151026 INS

1. Installer: neue Option `--with-sdr` für einen RTL-SDR-Dongle als S-Meter (installiert `rtl-sdr`, sperrt den DVB-Treiber, prüft den Dongle und ob ihn ein anderes Programm wie OpenWebRX benutzt). Der Log-Hinweis am Ende zeigt jetzt einen Befehl, der funktioniert. Der Installer wird mit `bash install.sh` gestartet (kein `chmod +x` nötig) und setzt `core.fileMode false`, damit `git pull` nicht mehr an Dateirechten scheitert.
2. README: Installer-Optionen, Fehlersuche, Kontakt/Feedback (Telegram). Handbücher: Hinweise zu Mikrofonverstärkung, Log und Kontakt.

### V-151026 SVC

1. Fehlerbehebung: Das Programm startet jetzt auch als Systemdienst (`ae5900.service`, z. B. nach dem Installer). Ohne Terminal brach es mit „The Werkzeug web server is not designed to run in production“ ab und startete in einer Schleife neu (weder HTTP noch HTTPS erreichbar). Nur von Hand im Terminal lief es.

### V-141026 BGD

1. Hintergrundbild: Das Repository enthält `static/bgr_default.jpg`. Dein eigenes Bild (CHANGE im Setup & Sync) wird als `static/bgr.jpg` gespeichert. Diese Datei wird von Git ignoriert, ein `git pull` kollidiert also nie damit. RESET stellt das Standardbild wieder her.

### V-141026 MOD

1. Korrektur des Hamlib/Rigctl Code bei Verwendung von Openwebrx als Client und S-SMETER
2. Moduswechsel über Hamlib/Rigctl beachten die Einstellungen Skip PA / Skip CW und springen nicht mehr in einen falschen Modus

### V-131026 SMT / BGR

1. Zusätzliche Implementierung: Verwendung eines RTL-SDR-Dongles mit dedizierter Antenne als S-Meter (nur das Paket `rtl-sdr` ist erforderlich)
2. Zusätzliche Implementierung: Verwendung eines OpenWebRX-Servers als S-Meter (ein dedizierter, privater, nicht öffentlicher OpenWebRX-Server ist erforderlich)
3. Upload-Funktion für Hintergrundbilder hinzugefügt (just for fun)

### V-121026 BAR

1. Bugfix - Firefox Mobile stocken beim Laden der Seite & IOS Freeze - Bitte testen
2. Anpassung der Audio-Tasten

### V-061026 CLS

1. Fehlerbehebung beim Clarifier

### V-051026 NDG – WebAudio-Update – BITTE TESTEN

1. WebAudio für weniger Verzögerungen (Lags) in mobilen Browsern neu konfiguriert
2. Kleine Fehlerbehebungen bei Puffer und Timing
3. Versuch, ein AudioWorklet/Ringpuffer-System zu implementieren (ähnlich wie bei OpenWebRX)

Bitte gib bei Rückmeldungen folgende Informationen an:
1. Soundkarte (oder die Ausgabe von: `pactl list short sources`)
2. Die Zeile „[AUDIO-ROUTING] Karte: ...“ aus dem Log
3. Browser und Version sowie die Info, ob der Ton in den ersten Sekunden ruckelt
4. Die Zeilen „Live:“ und „net:“ aus „Setup & Sync“ (Screenshot ist auch in Ordnung)
5. Hintergrundbetrieb / ausgeschalteter Bildschirm: Läuft der Ton weiter?

### V-041026 RMF *MEILENSTEIN UPDATE*

1. Neue Audio-Engine: ruhiger, weniger Verzögerung, korrigiert sich selbst. Rate und Puffer sind im Setup & Sync einstellbar.
2. Neue Soundkarten-Erkennung: funktioniert jetzt mit den meisten USB-Soundkarten, nicht nur mit C-Media.
3. S-SCAN / MW wartet nach Signalende 3 Sekunden, bevor es weitersucht. Das Tempo von SCROLL ist einstellbar.
4. Tasten- und Boxsteuerung (optional, standardmäßig aus): U/D = Kanal, M = Mode, A = ASQ, S = Scan (lang = Scroll), F7/F8 = Senden an/aus.
5. Weniger Datenverkehr beim Wasserfall.
6. Neuer Installer (install.sh): startet automatisch beim Booten, Mumble ist jetzt optional.

Zusatz: Bitte ae_5900_v2.py, index.html und install.sh aktualisieren und das Programm neu starten. Neue Stellschrauben findet ihr im Setup & Sync.

### V-300926 SWX

1. RX Audio - rebuild. Läuft auch im Hintergrund weiter.
2. S-SCAN / MW um SCROLL-Funktion erweitert. (Kanaldurchlauf bei offenem Squelch) Dazu lange auf die S-SCAN oder MW Taste drücken.

Zusatz: Bitte schaut euch im Setup & Sync um. Da sind neue Stellschrauben auch für den Wasserfall.

### V-290926 AFX

1. Audio Lautstärke Fix
Laute Peaks beim Verbinden wurden entfernt 

Zusatz: Bitte schaut euch im Setup & Sync um. Da sind neue Stellschrauben auch für den Wasserfall.

### V-270926 WBA

1. Wasserfall angepasst
2. Fehler beseitigt
3. WebAudio integriert über https/port 5443. Die Schalter für das Webaudio befinden sich im Setup & Sync Bereeich.

Zusatz: Bitte schaut euch im Setup & Sync um. Da sind neue Stellschrauben auch für den Wasserfall.

### V-250926 WFB

TESTING! Ich muss selber erst sehen, ob mir das gefällt.

1. Schüttel-Fehler in der Desktopansicht korrigiert.
2. Die Audio-Balken sind jetzt feiner dargestellt.
3. Im Setup & Sync kann man zwischen Audiobalken, so etwas ähnlichem wie einem Wasserfall oder beidem wählen.

### V-240926 BGF

Nach längerer, notwendiger Pause, hier zumindest einige Bugfixes.

1. S-Scan optimiert
2. Fehler in den CLAR +/- UP/DOWN behoben
3. A/SQ Res. gibt jetzt wieder ein visuelles Feedback.
4. Im PA stehen nun UP/DOWN zur Verfügung. Damit lässt sich blind die Lautstärke der physichen Gerätes korrigieren, falls zu leise oder zu laut.

### V-200726 BTVO

1. S-Meter über BT-Option
2. Stabilerer VFO
3. CH50-Bugfix

### V-090726 i3/a6 B-VFO

1. VFO-Modus hinzugefügt.
2. Video-Tutorials hinzugefügt.
3. Diverse Fehlerbehebungen in der Benutzeroberfläche.

### V-050726 i1/a9 RIGC

1. hamlib/rigctl-Funktionen hinzugefügt.
Abhängigkeiten installieren (sudo apt install libhamlib-utils)

2. Openwebrx TX-Button ist in openwebrx_ptt_code.txt verfügbar // zum Kopieren/Einfügen bereit.
3. install.sh angepasst.

### V-300626 i4/a1 DSPx

1. Automatische Anpassung der Anzeigegröße zwischen Smartphone und Computer.

### V-280626 i1/a1 BF

1. Fehlerbehebungen der V-240626

### V-240626 i1/a4 JS8

1. Neuimplementierung der JS8call-Steuerung.

Als Trigger in JS8call in Radio/Rigoptions (schaltet automatisch ein/aus) verwende:

```bash
curl -s http://127.0.0.1:5000/api/cmd/TX?state=%1
```
In anderen Digitalmodi verwende für TX:

```bash
curl -s http://127.0.0.1:5000/api/cmd/TX?state=%1
```
Für RX:

```bash
curl -s http://127.0.0.1:5000/api/cmd/TX?state=%0

```
2. VOX Bugfixes

### V-210626 i6/a9 BPLC

1. Alle Ländercodes hinzugefügt. Grüße an meine Tester in Polen und Großbritannien.
2. Erneut einige Fehlerbehebungen für FW 1.12-Nutzer.

### V-190626 i2/a5 CQRP

1. Neue Terminaltasten können unter „Einstellungen & Synchronisierung“ ausgewählt und bearbeitet werden.
2. Mit den Tasten können QSOs aufgezeichnet und wiedergegeben sowie CQ-Rufzeichen aufgezeichnet und wiederholt werden. Diese Funktion kann unter „Einstellungen & Synchronisierung“ aktiviert werden.
3. Fehlerbehbungen

### V-170626 i4/a1 FLK

1. Einige Bugfixes in der Benutzeroberfläche
2. A/SQ-Ebene zur Anzeige hinzugefügt. Bitte verwende zunächst A/SQ Res. (dauert etwa 25 Sekunden) und verwende dann die Tasten A/SQ +/-.
3. Unschöne Tastenbewegung behoben.

### V-150626 i4/a5 BTN

1. Fehlerbehebungen für Schaltflächen.

### V-120626 i1/a1 LN-RB

1. Roger-Piepton-Schalter hinzugefügt

### V-110626 i9/a9 LNG

1. Die Sprache des Handbuchs unter „Einrichtung & Synchronisierung“ ändert sich entsprechend der Browsersprache.

### V-110626 i8/a9 VX-RB-SM-MW

1. VOX-Funktion korrigiert
2. Rogebeep-Funktion implementiert
3. Simulationsmodus für Tests ohne Box hinzugefügt
4. MultiWatch-Fehler behoben
