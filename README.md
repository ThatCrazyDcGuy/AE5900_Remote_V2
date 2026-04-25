Eine komplexere LAN/Web-Fernsteuerung für das Albrecht AE-5900 Funkgerät, die das AMM-500 Mikrofon simuliert. Per Webbrowser bedienbar.
=======================================================

## Hauptziel des Projekts:

Entwicklung einer komplexeren LAN/Web-Fernsteuerung für das Albrecht AE-5900.
Es ist zwar nicht mit rigctl oder hamlib vergleichbar, aber es funktioniert.

Falls Du das Funkgerät nicht kennst: https://www.alan-electronics.de/product-details.aspx?WPParams=50C9D4C6C5D2E6BDA5A98494A895
Ich habe mein AE5900 von https://gmw-funktechnik.ch/, einem fantastischen Fachgeschäft für klassische CB- und Amateurfunkgeräte.

## Ein Bild erzählt dir mehr als deine Ehefrau

- Ein Screenshot vom aktuellen UI, im Browser, auf dem Smartphone

	![AE5900_Remote_v2](/pictures/webui.jpg)

- Ein Foto, ok, zwei Fotos vom Prototyp

	![AE5900_Remote_v2](/pictures/prototype2.jpg)

## Über das Gerät & Warum

Das Albrecht AE-5900 ist das fantastische neue (2026) FM/AM/SSB/CW-Funkgerät, mit dem ich nicht gerechnet hatte. Es bietet riesiges Potenzial für jede Menge Spaß und hat mich nach 35 Jahren Funkpause wieder zum CB-Funk zurückgebracht.

Also habe ich etwas Zusätzliches dafür gebaut, und jemand (ja, danke nochmal, Kumpel!) hat mir geraten, es auf GitHub zu veröffentlichen. Ich dachte mir: Na gut.

Das Gerät basiert auf einem FT232RL FT232 FTDI USB 3,3 V 5,5 V zu TTL Seriell Adapter, einer günstigen USB-Soundkarte, einem USB-Hub-Breakout-Board, Spulen, Widerständen, Kondensatoren und ein paar Teilen aus meiner Bastelkiste. Es funktioniert einwandfrei und macht mir viel Spaß. Mal sehen, was die nächsten Tage bringen.

Aber warum?

Es ist ein Hobby, für das man einfach nicht genug Zeit haben wird. Besonders, wenn man ein älterer Kerl mit Kindern, Garten, einem oder mehreren Jobs und all den anderen Überraschungen des Lebens. Jetzt kannst du deine Heimstation mit deiner perfekten, selbstgebauten Antenne sogar auf der Toilette deines Arbeitsplatzes oder wo auch immer nutzen.

Genau deshalb.

## So funktioniert es:

Schließe das Remote-Gerät an einen Raspberry Pi oder ein anderes Gerät an, auf dem das Python-Skript ausgeführt werden kann. Außerdem sollten Mikrofon- und Lautsprecherausgang des AE5900 angeschlossen sein. Starte Mumble auf dem Host-Rechner. Eventuell muss Ein- und Ausgang in den Linux-Audio-Settings getauscht werden. Führe die Datei `python3 ae_5900_v2.py` aus.

Rufe `localhost:5000` auf. Stelle an deinem AE5900 Mikrofon TYPE 2 ein, setze deine P1 - P4 Key-Shortcuts Halte die Sync-Taste im Websetup-Menü 3 Sekunden lang gedrückt.  Starte Mumble auf dem Remote-Gerät (Smartphone / Computer... was auch immer) und hab viel Spaß!


Das ist eigentlich alles und wer nicht komplett ahnungslos ist, bekommt das schon hin.

## Hardware-Bastelei

Der Part folgt noch, mit Bildern und allem was man wissen muss.

- Vorab mal die Komponenten für den Audiofilter und was man so zum Basteln nutzen kann:

	![AE5900_Remote_v2](/pictures/filterkomponenten.jpg)
	![AE5900_Remote_v2](/pictures/steuerungkomponenten.jpg)

- Ich habe euch ein schönes Bild gemalt. Sieht zwar aus wie von einem Dreijährigen gemalt, aber so verstehts jeder.

	![AE5900_Remote_v2](/pictures/overview_v2.png)
	![AE5900_Remote_v2](/pictures/audiofilter.jpg)

Man kann die USB Geräte natürlich auch einfach in einen USB Hub stecken, aber wo bleibt da der Spass am "so klein wie möglich" bauen?
Die beiden Filter muss man aber dennoch löten. 

Es ist auch mölich ohne Klinkenstecker das Audio des AE5900 abzugreifen. Der Mic Plug bietet die Pins EXT-AF und GND.
Hier gibt es aber 2 Proleme. Zumindest auf meinem AE5900 habe ich dort unschöne HF drauf. Will man dass das Gerät zu Hause stumm da steht, muss man dennoch einen Klinkenstecker als Terminator verwenden.

### Benötigte Software


Mumble & Mumble Server für die Audioübertragung
	
Tailscale auf all den Geräten die für dieses Projekt genutzt werden. :)

	# curl -fsSL https://tailscale.com/install.sh | sh

Dann wird in die Tasten gehauen oder der nachfolgende Krams einfach kopiert und eingefügt.

	# sudo apt update && sudo apt full-upgrade -y

	# sudo apt install git curl openssh-server python3-pyaudio python3-numpy python3-serial python3-flask pipewire pipewire-audio pipewire-alsa pipewire-pulse pipewire pipewire-audio-client-libraries pavucontrol wireplumber libpipewire-0.3-modules ladspa-sdk swh-plugins dbus-user-session mc htop
	# sudo apt remove pipewire-media-session

    # sudo usermod -a -G audio $USER
    # sudo usermod -a -G dialout $USER

    # mkdir ~/.config/pipewire/
    # mkdir ~/.config/pipewire/pipewire.conf.d/

    # mcedit ~/.config/pipewire/pipewire.conf.d/custom.conf

ADD:

context.properties = {
default.clock.rate = 48000
default.clock.allowed-rates = [ 44100 48000 88200 96000 ]
}


    # mkdir ~/.config/pipewire/pipewire-pulse.conf.d/
    # mcedit ~/.config/pipewire/pipewire-pulse.conf.d/99-disable-autogain.conf
ADD:

 pulse.rules = [
{
    matches = [
        { application.process.binary = "mumble" }
        { application.process.binary = "mumble-worker" }
    ]
    actions = { quirks = [ block-source-volume ] }
}
]

    # mcedit ~/.config/pipewire/pipewire-pulse.conf.d/block-autoscale.conf
ADD:

pulse.rules = [ { matches = [ { application.process.binary = "mumble" } ]; actions = { quirks = [ block-source-volume ] } } ]


## Los geht's!

Wenn die Hardware aufgebaut und alle Einstellungen vorgenommen sind, dann:

	# git clone https://github.com/ThatCrazyDcGuy/AE5900_Remote_V2

	# python3 ~/AE-5900_Remote_v1/webinterface/app.py

Updaten kann man dann jeweils mit:

	# git pull

Es empfiehlt sich, zu Hause einen WebSDR zu betreiben. Ich nutze ihn selbst. Nicht nur, um zu überprüfen, ob der richtige Kanal und Modus ausgewählt ist, sondern auch, um den Ton zu prüfen. Außerdem kannst du so die Vorgänge auf allen Kanälen verfolgen. Ein guter WebSDR lässt sich einfach mit OpenWebRX, einem Raspberry Pi, einem RTL-SDR-Dongle (z. B. RTL-SDR Blog V3 oder V4 / Nooelec NESDR V5) und einer Antenne aufbauen.

Schau dir einfach OpenwebrxPlus an: https://luarvique.github.io/ppa/ RTL-SDR Blog v4: https://www.rtl-sdr.com/v4/

## Was du sonst noch erwarten kannst:

Nichts weiter als meine Erfahrung.
Ich werde keinen persönlichen Support anbieten.
Aber ich werde einige Skripte, Bilder und Ideen hochladen, um sie mit anderen zu teilen.

Ich bin kein Programmierer, aber ich kann Texte lesen, verstehen und in meine Projekte einbauen.



