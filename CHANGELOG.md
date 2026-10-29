# Changelog

Deutsch: [CHANGELOG_DE.md](CHANGELOG_DE.md) · Back to the [README](README.md)

Always update with `git pull`, then restart the program.

Note: some version labels in older entries were corrected (the date part is DDMMYY).

### V-291026 AUD (current)

1. Fix: "CQ REC" recorded only an empty file (44 bytes). The recorder looked for the old Mumble connection and never found the microphone stream of the WebUI, so it recorded silence. It now connects to the microphone stream (it keeps trying while recording) and the log tells you if it cannot find one. The browser microphone (🎤) must be running while you record.
2. New: microphone selection (Setup & Sync -> Audio). "Device microphone" uses the phone's or computer's own microphone, so a Bluetooth headset is no longer forced into hands-free mode (poor sound) when you start the microphone. You can also pick any single input. Stored per device; falls back to the system default if the chosen one is not available. Tested on Android and desktop; browsers that do not allow a choice (iPhone/Safari) keep using the default - feedback from iPhone users is still pending.
3. New: audio output selection (Setup & Sync -> Audio). The received audio can be played on a chosen device of the computer, for example the monitor of the sound card or a virtual audio cable, so WSJT-X or JS8Call on the same computer can decode it without further tools. Tested with WSJT-X and JS8Call on Ubuntu with Brave, Chrome and Firefox. Needs a browser that supports choosing the output (Chrome, Edge, Brave, current Firefox on the desktop).

### V-281026 WFS

1. RF waterfall and S-meter are independent now: you can use the ESP32 S-meter together with the OpenWebRX (or SDR dongle) waterfall. A new selection "RF waterfall source" sits in Setup & Sync -> Display & background, together with all waterfall options (on/off, span, "keep running while transmitting"). Switching the S-meter source no longer touches the waterfall, so the display mode does not have to be changed a second time. OpenWebRX is only contacted while the waterfall is switched on and someone is watching it. Existing installations keep the behaviour they had (the waterfall uses the S-meter source) until you choose a source.
2. The waterfall message on the display now names the chosen source and shows its state (for example "waiting for OpenWebRX data ... (connected, waiting for config)").

### V-281026 SET

1. S-meter, hardware mod (ESP32): new calibration. In Setup & Sync -> S-meter & RF waterfall you now find Floor (0 %) and Full (100 %) with the live reading of the ESP32 and the "= now" buttons, plus RESET (60 / 98). Before, the values 60 and 98 were fixed in the program. The ESP32 itself sends only 0-100, so the resolution is about 38 steps; the firmware is unchanged.
2. Roger beep: your own sounds can be uploaded (UPLOAD next to the selection). Any common audio file (WAV, MP3, OGG, M4A, up to 5 seconds) is converted in the browser to a small mono WAV. A play button lets you listen to a beep on the device you use; your own beeps can be deleted again. They are stored as `beeps/user_NAME.wav` (add `beeps/user_*.wav` to `.gitignore`). The beep setting is now checked on the server (only existing files).
3. Setup & Sync is tidied up into collapsible sections: Radio & keys, Audio, Display & background, S-meter & RF waterfall, Camera, Security, and the status correction. Several sections can be open at the same time, so you can keep the camera preview in view while adjusting settings. Which sections are open is remembered per device. Nothing was removed.
4. 4th key row: swipe left/right on the row, or use the two slim arrows beside it, to switch between P1-P4, REC/CQ and the custom keys. The choice is stored on the server and applies to all devices at once; no page reload any more. Works the same on phone, tablet and desktop.

### V-231026 PWD

1. Security: the web interface is now protected by a password. After the update the page asks you to set one at the first visit (only possible from your own network: LAN, Tailscale or the Raspberry Pi itself). A semi-transparent window sits above the interface until you have logged in. The password is stored only as a hash in `config.json` (new keys `auth_hash`, `auth_secret`, `api_key`), the login is remembered for 30 days per device, and wrong passwords are slowed down (5 tries, then 30 s, 60 s, 120 s ... up to 15 minutes per address). Setup & Sync has a new "Security" block: change the password (this logs out all other devices), log out, and the key for other programs. The installer can ask for the password too (`bash install.sh --with-password`, or answer the question at the end). Forgotten: `python3 ae_auth.py --set-password` on the Raspberry Pi (stop the program first: `systemctl --user stop ae5900`).
2. What is protected: everything except the page itself, i.e. all `/api/...` calls, the WebSocket (audio, microphone, waterfall) and the camera. The camera page `/cam` and the pop-out link work after you have logged in on that device. Requests that a web page from another site sends in your browser are always refused (this closes the way for "drive-by" attacks from the internet while you browse, also without a password). The terminal commands of the custom keys are no longer sent to anyone who is not logged in, and can only be changed after logging in.
3. Tools on **other** computers: the PTT calls (`/api/rig/ptt/0|1` and `/api/cmd/TX?state=...`) need a key now, because they cannot log in: add `?key=KEY` (or `&key=KEY`), or send it as the header `X-API-Key`. You find the key in Setup & Sync -> Security (SHOW). The key allows PTT only, nothing else. Programs on the Raspberry Pi itself (127.0.0.1), for example `curl` from JS8Call on the Pi, work as before without a key. The OpenWebRX PTT button in the Hamlib/OpenWebRX handbook now has a `ALBRECHT_KEY` line for the key.
4. Not protected, because these protocols have no login: the Hamlib/rigctl port 4532 and the digimode UDP port 2442. Never make them reachable from the internet. The README now lists all ports and what they do.
5. The secret that signs the login (replacing the fixed word in the program) is created individually on each installation. `config.json` is set to readable by the owner only.

### V-221026 LAY

1. The three-column layout that users liked on the phone in landscape mode is now also the desktop layout (number pad left, display and function keys in the middle, PTT and audio buttons on the right). On large screens it is centred and limited to 1560 px, with clearly larger text and buttons (about 20 % larger than on the phone, so it is easy to read from a distance). The enlargement applies only to real desktop screens (mouse); phones and tablets in landscape keep their size, portrait is unchanged.

### V-221026 TLS

1. Fix: HTTPS (port 5443) no longer dies after a network change, a dropped connection or a Tailscale reload on a phone. The cause: the web server did the TLS handshake in the loop that accepts connections, so one half-finished connection blocked every further HTTPS connection (plain HTTP kept working, only a restart helped). Now every connection does its handshake in its own thread with a 10 s time limit, and dead connections are cleaned up by TCP keep-alive. Reproduced and checked with a test setup (stalled, garbage and half-open connections); the live WebSocket/microphone part over HTTPS still has to be checked on a real device.
2. Microphone safety: if the microphone disappears while "Talk (mic)" is active (incoming phone call, another app takes the microphone, permission revoked), the browser now switches the microphone off and releases PTT, instead of carrying on without modulation. The button then shows "Mic lost (call?)".

### V-211026 UIS

1. Display settings are now stored in `config.json` and apply on all your devices as soon as you change them once: the display mode (Bars / Waterfall / Both / RF waterfall), the contrast and speed of the audio waterfall and the contrast of the RF waterfall. Until the program has stored a value, the value your browser had remembered is still used, so nothing is lost. The S-meter source and the RF waterfall switches were already stored in `config.json`. Audio settings and keyboard shortcuts stay per device on purpose.

### V-211026 OWF

1. RF waterfall with OpenWebRX as S-meter source: the program now also takes the waterfall rows from your OpenWebRX (spectrum of its whole profile, cut to the window around the channel). So it works without a dongle of its own, e.g. when OpenWebRX already uses the dongle. The display mode "RF waterfall" and the settings (width, contrast) are the same as with the dongle. Your own transmissions are always shown (marked red), because OpenWebRX is only listening. The resolution depends on the OpenWebRX profile (sample rate / FFT size), so it can be coarser than with a dongle of its own. Not tested against a real OpenWebRX yet.

### V-211026 RFF

1. RF waterfall display: the green line on the current channel is gone (it covered the signal). The triangle at the top marks the centre; the channel number and the grey neighbour lines stay.

### V-211026 RFE

1. Fix: in the display mode "RF waterfall" the waterfall now scrolls the same way as the normal waterfall (the new rows did not stay visible on some devices). The triangle marker at the top (centre of the window = the current channel) is shown again, as in "Both".

### V-211026 RFD

1. The RF waterfall is now a fourth DISPLAY MODE (SETUP & SYNC -> Display mode -> "RF waterfall (SDR dongle)"). It fills the whole display from edge to edge, with the channel grid marked (current channel green, number above the S-meter bar) and your own transmissions marked red at the left edge when "keep running while transmitting" is on. The choice is remembered per browser; selecting it switches the waterfall on in the program (it still only calculates while a browser is watching). It needs the S-meter source "SDR dongle" - otherwise the display says so. Width and contrast are set in the SDR section.

### V-211026 WFL

1. RF waterfall (optional, off by default) in SETUP & SYNC: with the S-meter source "SDR dongle" a second display shows the radio spectrum around the current channel, so you can see QSOs on the neighbouring channels. The window (40 / 60 / 100 / 200 kHz wide) is centred on the channel; the channel grid is marked, the current channel in green. The colours follow the noise floor automatically, "Contrast" sets the range. It uses the IQ data the S-meter already reads from the dongle; nothing is calculated and nothing is sent while the waterfall is switched off or not open. Needs roughly 10-15 % of one Raspberry Pi 3 core while open (estimate, not measured).
2. Optional "keep running while transmitting": the dongle is then not released during TX, so your own signal appears in the waterfall (marked red at the left edge). Only with a separate receive antenna at some distance. Never connect the dongle to the transmit antenna or the antenna socket of the radio. The S-meter value is not updated during TX.

### V-201026 CAM

1. Camera in SETUP & SYNC (optional, off by default): watch your radio with a USB webcam. A drop-down lists the cameras found, plus resolution (320x240 / 640x480 / 1280x720), horizontal flip and vertical flip. PREVIEW shows the picture in place; `/cam` shows the picture only (for a second screen or a bookmark). It needs no OpenCV, only the package `ffmpeg` (`sudo apt install ffmpeg`, or `bash install.sh --with-cam`). ffmpeg only runs while someone is watching, so a switched-off camera causes no load and no network traffic. The camera has to deliver MJPEG (practically every USB webcam does).
2. Start check: if a required Python package is missing, the program now prints the exact `sudo apt install ...` line instead of a traceback. Optional programs (ffmpeg, rigctld, rtl_sdr) are reported at start only when the matching function is switched on.

### V-181026 LSC

1. Smartphone landscape mode: in landscape orientation the layout has three columns. Left: keypad with CLAR +/STEP/CLAR - above MIC +/RB/MIC -. Middle: display and function keys. Right: PTT and the two audio buttons. SETUP & SYNC stays below the layout. Portrait mode and the desktop layout are unchanged.

### V-151026 INS

1. Installer: new option `--with-sdr` for an RTL-SDR dongle as S-meter (installs `rtl-sdr`, blocks the DVB driver, checks the dongle and whether another program such as OpenWebRX uses it). The log hint at the end now shows a command that works. The installer is started with `bash install.sh` (no `chmod +x` needed) and sets `core.fileMode false`, so `git pull` is no longer blocked by file permissions.
2. README: installer options, a troubleshooting section, contact/feedback (Telegram). Handbooks: notes on microphone gain, log and contact.

### V-151026 SVC

1. Bugfix: the program now also starts as a system service (`ae5900.service`, e.g. after the installer). Without a terminal it stopped with "The Werkzeug web server is not designed to run in production" and restarted in a loop (HTTP and HTTPS both missing). It worked only when started by hand in a terminal.

### V-141026 BGD

1. Background image: the repository ships `static/bgr_default.jpg`. Your own image (CHANGE in Setup & Sync) is stored as `static/bgr.jpg`, which is ignored by git, so `git pull` never conflicts with it. RESET returns to the default image.

### V-141026 MOD

1. Correction of Hamlib/Rigctl code when using Openwebrx as client and S-SMETER
2. Mode changes via Hamlib/Rigctl respect the Skip PA / Skip CW settings and no longer jump to a wrong mode

### V-131026 SMT / BGR

1. Additional implementation: Use RTL-SDR dongle with dedicated antenna as an S-meter (only the `rtl-sdr` package is required)
2. Additional implementation: Use OpenWebRX server as an S-meter (a dedicated, private, non-public OpenWebRX server is required)
3. Added a background image uploader (just for fun)

### V-121026 BAR

1. Bug fix – Firefox Mobile stuttering during page load & iOS freeze – Please test
2. Audio button adjustments

### V-061026 CLS

1. Clarifier bugfix

### V-051026 NDG - WebAudio update - PLEASE TEST

1. WebAudio reconfigured for less lags on mobile browsers
2. Small bugfixes in buffer and timing
3. Tried to implement an AudioWorklet/Ringpuffer like you might know from openwebrx

When you report, please include:
1. Sound card (or the output of: pactl list short sources)
2. The "[AUDIO-ROUTING] Karte: ..." line from the log
3. Browser + version, and whether audio stutters in the first seconds
4. The "Live:" and "net:" lines from Setup & Sync (screenshot is fine)
5. Background / screen-off: does the audio keep running?

### V-041026 RMF *MILESTONE UPDATE*

1. New audio engine: smoother, lower latency, self-correcting. Rate and buffer settings are adjustable in "Setup & Sync."
2. New sound card detection: now works with most USB sound cards, not just C-Media devices.
3. S-SCAN / MW: waits 3 seconds after the signal ends before resuming the search. SCROLL speed is adjustable.
4. Key and control box support (optional; disabled by default): U/D = Channel, M = Mode, A = ASQ, S = Scan (long press = Scroll), F7/F8 = TX on/off.
5. Reduced data traffic for the waterfall display.
6. New installer (install.sh): starts automatically on boot; Mumble is now optional.

Note: Please update ae_5900_v2.py, index.html, and install.sh, then restart the program. You can find new configuration options in "Setup & Sync."

### V-300926 SWX

1. RX audio rebuilt; continues running in the background.
2. SCROLL function added to S-SCAN / MW (channel scanning with squelch open). To activate, press and hold the S-SCAN or MW button.

Note: Please take a look at the Setup & Sync section. There are new settings available, including for the waterfall.

### V-290926 AFX

1. Audio volume fix
Loud spikes upon connecting have been removed.

Note: Please take a look at the "Setup & Sync" section. There are new settings available there, including options for the waterfall display.

### V-270926 WBA

1. Waterfall adjusted
2. Bug fixes
3. WebAudio integrated via HTTPS/port 5443. The controls for WebAudio are located in the Setup & Sync section.

Note: Please take a look around the Setup & Sync area. There are new settings there, including some for the waterfall.

### V-250926 WFB

TESTING! I need to see for myself if I like this.

1. Fixed a "shaking" glitch in the desktop view.
2. Audio bars are now rendered with finer detail.
3. In Setup & Sync, you can choose between audio bars, a waterfall-like display, or both.

### V-240926 BGF

After a long, necessary hiatus, here are at least a few bug fixes.

1. S-Scan optimized.
2. Fixed errors in CLAR +/- UP/DOWN controls.
3. A/SQ Res. now provides visual feedback again.
4. UP/DOWN controls are now available in PA mode. This allows for blind adjustment of the physical device's volume if it is too quiet or too loud.

### V-200726 BTVO

1. S-meter via BT option
2. More stable VFO
3. CH50 bug fix

### V-090726 i3/a6 B-VFO

1. VFO Mode added.
2. Video tutorials added
3. Some bugfixes in UI

### V-050726 i1/a9 RIGC

1. hamlib/rigctl functions added.
   install dependencies (sudo apt install libhamlib-utils)

2. Openwebrx TX-Button is available in openwebrx_ptt_code.txt // copy/paste ready.
3. New install.sh added.

### V-300626 i4/a1 DSPx

1. Automatic adjustment to the display size between smartphone and computer.

### V-280626 i1/a1 BF

1. Bugfixes für V-240626

### V-240626 i1/a4 JS8

1. Reimplementation of JS8call control.
   
 As trigger in JS8call in Radio / Rigoptions (will switch on/off automatically) use:

```bash
curl -s http://127.0.0.1:5000/api/cmd/TX?state=%1
```
 In other digimodes use for TX:
  ```bash
  curl -s http://127.0.0.1:5000/api/cmd/TX?state=%1
```
 For RX:
 
   ```bash
    curl -s http://127.0.0.1:5000/api/cmd/TX?state=%0
```

Replace 127.0.0.1 with your ip.
You can also build a on/off script with these commands.

2. VOX bugfixes

### V-210626 i6/a9 BPLC

1. ALL country codes added. Greetings to my testers in Poland and Great Britain.
2. Again, some Bugfixes for FW 1.12 users.

### V-190626 i2/a5 CQRP

1. New terminal keys can be selected and edited in Setup & Sync.
2. Keys can be used to record and play back QSOs, as well as to record and repeat CQ calls. This function can be selected in Setup & Sync.
3. Bugfixes

### V-170626 i4/a1 FLK

1. Some bugfixes in UI.
2. A/SQ level to display added. Please first use A/SQ Res. (will run about 25sec) then use the A/SQ +/- buttons.
3. Ugly movement of buttons fixed.

### V-150626 i4/a5 BTN

1. Button bugfixes.

### V-120626 i1/a1 LN-RB

1. Roger beep switch added.

### V-110626 i9/a9 LNG

1. The language of the manual under Setup & Sync changes according to the browser language setting.

### V-110626 i8/a9 VX-RB-SM-MW

1. VOX function fixed.
2. Rogebeep function implemented.
3. Simulation mode added for testing without the box.
4. MultiWatch fixed.
