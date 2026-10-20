# AE5900 Remote Control V2

Wechsle Sprache zu DE: [🇩🇪 Deutsch](https://github.com/ThatCrazyDcGuy/AE5900_Remote_V2/blob/main/README_DE.md)

## ENGLISH VERSION OF README

A LAN/Web Remote Rig Control System for the Albrecht AE-5900 radio, simulating the AMM-500 microphone. This allows the AE5900 to be operated via a web browser in a webinterface.

### The Foreword:

**WARNING!!!** There is a risk that using this equipment may be illegal, depending on the laws of your country.
Consider this with your conscience. I'm not your mother!

### Main Goal of the Project:

Development of a sophisticated LAN/web remote control for the Albrecht AE-5900.
Ultimately, the purpose is also to revive CB radio and make it more attractive.
Flexible solutions provide better access. And that's exactly what this project should enable.

### A picture will tell you more than your wife:

- A screenshot of the current UI, in the browser, on your smartphone

![AE5900_Remote_v2](/pictures/webui_last.jpg)

1. Visual audio feedback (bars, waterfall or both)
2. Adjustable microphone volume
3. Optimized scan function with adjustable speed
4. Clarifier
5. Lock
6. Mute
7. Vox
8. MW (multi channel scan)
9. Squelch // Autosquelch
10. PTT kill switch activates after 30 seconds following connection loss.
11. Own roger beeps. Just add them to folder beeps.
12. Physical PTT key / special key on phone or keyboard
13. Country codes must be set in the web interface and on the device.
14. Hamlib/Rigctl compatible (flrig, fldigi, rigctl, grig, openwebrx, js8call & wsjt-cb)
15. S-meter from an RTL-SDR dongle or from your own OpenWebRX server
16. If you decide to open and solder the device, an external S-METER can be used via Bluetooth (ESP32).
17. Web Audio HTTP RX only / HTTPS RX and TX
18. Change the background image for individual style (just for fun)

> **Important:** Use the web interface on **one device at a time**. Hamlib/Rigctl software (e.g. OpenWebRX, fldigi) next to one browser is fine. Several browsers or phones controlling the radio at the same time are not: the PTT kill switch at connection loss can no longer work reliably then.

- Various features are demonstrated here. Rigctl and hamlib are implemented, and a Bluetooth S-meter.

[![AE5900 Webinterface V2 ](https://img.youtube.com/vi/0-UP0ARVENU/0.jpg)](https://www.youtube.com/watch?v=0-UP0ARVENU)

- A photo of the newest prototype without jack connector. All audio & control over RJ45.

![AE5900_Remote_v2](/pictures/v218mar2.jpeg)

### Minimum requirements for this project:

1. Ability to read
2. Ability to understand
3. Ability to implement
4. Soldering experience
5. Raspberry Pi 3
6. A little spare cash for the parts

### The Hardware Build

Includes pictures and everything you need to know.

- First, here are the components for the audio filter and what you can use for the build. I had most of these in my parts bin.

For the audio filter, we are using:

1. 1x 600:600 Ohm transformer
2. 1x 100 Ohm resistor
3. 1x 10 kOhm resistor
4. 1x 10nF (103) ceramic capacitor (at least one to filter out RF)
5. 1x 10µF electrolytic capacitor (approx. 16–50V)

Remaining components:

1. USB breakout board or a hub
2. FT232RL FTDI USB to TTL serial adapter (3.3V/5V)
3. USB sound card
4. RJ45 terminal
5. Metal enclosure

![AE5900_Remote_v2](/pictures/allpartsv2.jpg)

- I've drawn a nice picture for you. It might look like the work of a three-year-old, but this way, any hobbyist or soldering iron owner should be able to understand it.

![AE5900_Remote_v2](/pictures/overview_v3.png)

Of course, you could simply plug the USB devices into a USB hub, but where's the fun in building something as compact as possible?
You still have to solder the two filters, though.

#### How is this actually possible?

The AMM-500 sends serial HEX codes to the AE-5900, and the AE-5900 responds accordingly. This opens up a wide range of possibilities.
To realize this DIY project, I had to monitor the communication between the two devices.
Principle: Man-in-the-middle.

Since the AE-5900 only enables its codes after a handshake with the AMM-500, I first had to purchase the latter and eagerly await its arrival.

#### Required Software // Installation

This block loads the script and system updates onto the Raspberry Pi.
Then, all necessary components (Python, audio support, Tailscale and optionally Mumble) are installed.

Simply copy the entire block into the console.

```bash
git clone https://github.com/ThatCrazyDcGuy/AE5900_Remote_V2
cd ~/AE5900_Remote_V2/
bash install.sh
reboot
```

During the installation Tailscale shows a login link. Open it in a browser and follow the instructions.
The installer has a few options, see `bash install.sh --help`:

- `--with-sdr`: also set up an RTL-SDR dongle as S-meter
- `--with-mumble`: also install Mumble (optional, WebAudio does not need it)
- `--no-tailscale`: skip Tailscale (then only HTTP on port 5000, no HTTPS)
- `--no-service`: no autostart service

You can run the installer again at any time; it only repairs what is missing. Its log is `~/ae5900-install.log`.

Update later with `git pull` and restart the program. Your own settings (`config.json`) and your own background image are not touched.

### How it works:

1. Connect the DIY device to a Raspberry Pi or another host computer capable of running the Python script. This device then acts as the server.
2. Connect the adapter to the microphone port.
3. To mute the speaker, insert a dummy jack plug into the PA/EXT output.
4. Turn up the AE-5900's output volume from 0 to approximately 75% using the volume control.
5. Ensure proper grounding to avoid RF interference.
6. Ideally, the AE5900 should already be set to FM and channel 1.
7. Set the microphone type to "TYPE 2" on your AE5900 and configure your P1–P4 key shortcuts.
8. Run `python3 ae_5900_v2.py` on the host machine/server (the installer already starts it automatically at boot).
9. Open `http://HOSTNAMEIP:5000` or `https://HOSTNAMEIP:5443` in your browser on your client device. You should now have control over your AE5900.
10. Open the "Setup" section at the very bottom of the WebUI and perform the sync.
11. Set the labels for the P1–P4 buttons to match the settings on your AE5900.
12. You may need to make adjustments in the volume control (pavucontrol) on the host machine. Typical adjustments include setting your network-connected sound card as the default sound card under the "Configuration" tab.

The script supports all regions, including VFO mode.

That's basically it; anyone with a basic level of technical knowledge should be able to get this working.

### Audio Setup (especially for those wishing to use Mumble instead of WebAudio):

[Audio setup (AUDIOSETUP.md)](AUDIOSETUP.md)

### HAMLIB / OpenWebRX Control Setup:

[Hamlib / Rigctl / OpenWebRX (HAMLIBOWRX.md)](HAMLIBOWRX.md)

### S-Meter (three sources):

Choose the source in "Setup & Sync" under "S-Meter source": the ESP32 hardware mod, an RTL-SDR dongle, or your own OpenWebRX server.

[S-meter setup (SMETER.md)](SMETER.md)

### Bluetooth S-Meter Soldering Instructions and Setup:

[Bluetooth S-meter (BTSMETER.md)](BTSMETER.md)

### It's a good idea to run a WebSDR at home to check your installation if necessary (channel/modulation).
A good WebSDR can be easily set up with OpenWebRX, a Raspberry Pi, an RTL-SDR dongle (e.g., RTL-SDR Blog V3 or V4 / Nooelec NESDR V5), and an antenna.

Check out OpenwebrxPlus: https://luarvique.github.io/ppa/ RTL-SDR Blog v4: https://www.rtl-sdr.com/v4/

### Troubleshooting

- **No transmit audio?** Check the microphone gain on the AE5900 itself. "MIC +/-" in the web interface only controls the sound card; the microphone gain of the device must not be set to 0. Transmitting with the phone microphone needs HTTPS (port 5443).
- **Is the program running?** `systemctl --user status ae5900`
- **Read the log:** `sudo journalctl _SYSTEMD_USER_UNIT=ae5900.service -f` (without `sudo`, `journalctl --user` stays empty on Raspberry Pi OS)
- **Restart:** `systemctl --user restart ae5900`
- **`git pull` refuses to update ("local changes" in `install.sh`)?** Run `git config core.fileMode false` once (an earlier `chmod +x` changed the file permissions), then `git pull` again. If it still complains: `git checkout -- install.sh`. Your own settings (`config.json`) and background image are not affected.
- **Installer problems:** the log is `~/ae5900-install.log`.
- **Asking for help:** please post in the Telegram channel (see Contact / Feedback below): what you did, the relevant log lines (e.g. `[AUDIO-ROUTING] Karte: ...`), your sound card (`pactl list short sources`) and your browser + version.

### What's Still Missing // What Doesn't Work Yet

1. There's always something missing. What isn't there, will come later.

### Version Info & Changelog

Current: **V-201026 CAM** Always update with `git pull`.

1. Camera in SETUP & SYNC (optional, off by default): watch your radio with a USB webcam. A drop-down lists the cameras found, plus resolution (320x240 / 640x480 / 1280x720), horizontal flip and vertical flip. PREVIEW shows the picture in place; `/cam` shows the picture only (for a second screen or a bookmark). It needs no OpenCV, only the package `ffmpeg` (`sudo apt install ffmpeg`, or `bash install.sh --with-cam`). ffmpeg only runs while someone is watching, so a switched-off camera causes no load and no network traffic. The camera has to deliver MJPEG (practically every USB webcam does).
2. Start check: if a required Python package is missing, the program now prints the exact `sudo apt install ...` line instead of a traceback. Optional programs (ffmpeg, rigctld, rtl_sdr) are reported at start only when the matching function is switched on.

The complete history is in the [CHANGELOG](CHANGELOG.md).

### Extras and Test Runs

1. JS8Call works quite well with it. Of course, you have to play around with the settings a bit and enable VOX.
But it should be simple to add a PTT function for the appropriate software.

2. User feedback from April 30, 2026: Linux Mint around version 21.3 and below don't understand the Python Vol- and Vol+.
Just in case someone tests on such a system. A mint upgrade helps solve the problem.

### What Else to Expect:

Nothing more than my experience.
I will not provide personal support.
But I will upload some scripts, images, and ideas to share with others.

I am not a programmer, but I can read, understand, implement, and incorporate texts into my projects.

I take no responsibility for your builds. For my dear beta tester and me, both software and hardware work flawlessly.
The audio received consistently good feedback in QSOs.

### Thanks Bro's

Special thanks going out to all the referring sites I've seen these days:

- [blog.adafruit.com](https://blog.adafruit.com/2026/06/28/a-remote-web-rig-control-system-for-the-albrecht-ae-5900-radio-hamsunday/)
- [korben.info](https://korben.info/il-a-transforme-sa-radio-cb-en-station-pilotable-depuis-un-navigateur-web.html)
- [hackaday.com](https://hackaday.com/2026/06/03/web-based-control-for-a-cb-radio/)
- [daily.dev](https://daily.dev/posts/web-based-control-for-a-cb-radio-hvgarjfyn)
- [radiowalkietalkie.com](https://www.radiowalkietalkie.com/news/cb-radio-web-remote-control-solution-85555228.html)
- [bingo01](https://bingo01.de/)
- [simonthewizard.com](https://simonthewizard.com/)

Where the people talking about:

- [cb-lounge.de](https://forum.cb-lounge.de/)
- [funkbasis.de](https://www.funkbasis.de/)
- [cbfunk.ch](https://cbfunk.ch/)
- [cbfunker.online](https://cbfunker.online/)
- [worldwidedx.com](https://www.worldwidedx.com/threads/web-control-of-cb-radio.271268/#post-872377)

### Contact / Feedback

News, updates and your feedback: [t.me/gz62cb](https://t.me/gz62cb)
