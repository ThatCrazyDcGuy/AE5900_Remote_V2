# Changelog

Deutsch: [CHANGELOG_DE.md](CHANGELOG_DE.md) · Back to the [README](README.md)

Always update with `git pull`, then restart the program.

Note: some version labels in older entries were corrected (the date part is DDMMYY).

### V-141026 BGD (current)

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
