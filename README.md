# AE5900 Remote Control V2

Wechsle Sprache zu DE: [🇩🇪 Deutsch](https://github.com/ThatCrazyDcGuy/AE5900_Remote_V2/blob/main/README_DE.md)

## ENGLISH VERSION OF README

A LAN/Web Remote Rig Control System for the Albrecht AE-5900 radio, simulating the AMM-500 microphone. This allows the AE5900 to be operated via a web browser in a webinterface.
=======================================================

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

1. Visual audio feedback
2. Adjustable microphone volume
3. Optimized scan function with adjustable speed
4. Clarifier
5. Lock
6. Mute
7. Vox
8. MW (multi chanel scan)
9. Squelch // Autosquelch
10. PTT kill switch activates after 30 seconds following connection loss.
11. Own roger beeps. Just add them to folder beeps.
12. Physically PTT key / Special key on phone or keyboard
13. Country codes must be set in the web interface and on the device.
14. Hamlib/Rigctl compatible (flrig, fldigi, rigctl, grig, openwebrx, js8call & wsjt-cb)
15. RTL Dongle or OpenWebRX S-meter implementation
17. If you decide to open and solder the device, extrenal S-METER can now be used via Bluetooth.
18. Web Audio HTTP RX only / HTTPS RX and TX


- Various features are demonstrated here. Operable via multiple software and devices simultaneously. Also rigctl and hamlib is implemented and a bluetooth s-meter.

[![AE5900 Webinterface V2 ](https://img.youtube.com/vi/0-UP0ARVENU/0.jpg)](https://www.youtube.com/watch?v=0-UP0ARVENU)

- A photo of the newest prototype without jack conector. All audio & control over RJ45.

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

- I’ve drawn a nice picture for you. It might look like the work of a three-year-old, but this way, any hobbyist or soldering iron owner should be able to understand it.

![AE5900_Remote_v2](/pictures/overview_v3.png)

Of course, you could simply plug the USB devices into a USB hub, but where’s the fun in building something as compact as possible?
You still have to solder the two filters, though. 

#### How is this actually possible?

The AMM-500 sends serial HEX codes to the AE-5900, and the AE-5900 responds accordingly. This opens up a wide range of possibilities.
To realize this DIY project, I had to monitor the communication between the two devices.
Principle: Man-in-the-middle.

Since the AE-5900 only enables its codes after a handshake with the AMM-500, I first had to purchase the latter and eagerly await its arrival.

#### Required Software // Installation

This block loads the script and system updates onto the Raspberry Pi.
Then, all necessary components—such as Python, Mumble, audio support, and Tailscale—are installed.

Simply copy the entire block into the console.

```bash
git clone https://github.com/ThatCrazyDcGuy/AE5900_Remote_V2
cd ~/AE5900_Remote_V2/
sudo chmod +x install.sh
./install.sh
#If you want to use Tailscale:
#Copy the generated Tailscale link into your browser and follow the instructions
reboot
```

### How it works:

1. Connect the DIY device to a Raspberry Pi or another host computer capable of running the Python script. This device then acts as the server.
2. Connect the adapter to the microphone port.
3. To mute the speaker, insert a dummy jack plug into the PA/EXT output.
4. Turn up the AE-5900's output volume from 0 to approximately 75% using the volume control.
5. Ensure proper grounding to avoid RF interference. 6. Ideally, the AE5900 should already be set to FM and channel 1.
7. Set the microphone type to "TYPE 2" on your AE5900 and configure your P1–P4 key shortcuts.
8. Run `python3 ae_5900_v2.py` on the host machine/server.
9. Open `http://HOSTNAMEIP:5000` or `https://HOSTNAMEIP:5443` in your browser on your client device. You should now have control over your AE5900.
10. Open the "Setup" section at the very bottom of the WebUI and perform the sync.
11. Set the labels for the P1–P4 buttons to match the settings on your AE5900.
12. You may need to make adjustments in the volume control (pavucontrol) on the host machine. Typical adjustments include setting your network-connected sound card as the default sound card under the "Configuration" tab.

The script supports all regions, including VFO mode.

That’s basically it; anyone with a basic level of technical knowledge should be able to get this working.

### Audio Setup (especially for those wishing to use Mumble instead of WebAudio):

![AE5900_Remote_v2](AUDIOSETUP.md)

### HAMLIB / Openwebrx Control Setup:

![AE5900_Remote_v2](HAMLIBOWRX.md)

### Bluetooth S-Meter Soldering Instructions and Setup:

![AE5900_Remote_v2](BTSMETER.md)

### It's a good idea to run a WebSDR at home to check your installation if necessary (channel/modulation).
A good WebSDR can be easily set up with OpenWebRX, a Raspberry Pi, an RTL-SDR dongle (e.g., RTL-SDR Blog V3 or V4 / Nooelec NESDR V5), and an antenna.

Check out OpenwebrxPlus: https://luarvique.github.io/ppa/ RTL-SDR Blog v4: https://www.rtl-sdr.com/v4/

### What's Still Missing // What Doesn't Work Yet

1. There's always something missing. What isn't there, will come later.

2. ....

### Version Info & Changelog (always perform updates with 'git pull')

Current: 131026 SMT - TEST RUN -

- Additional implementation: Use RTL-SDR dongle with dedicated antenna as an S-meter (rtl-sdr and pyrtlsdr packages required)
- Additional implementation: Use OpenWebRX server as an S-meter (a dedicated, private, non-public OpenWebRX server is required)

Previous version: V-121026 BAR

1. Bug fix – Firefox Mobile stuttering during page load & iOS freeze – Please test
2. Audio button adjustments

Previous version: V-061026 CLS

1. Clarifier bugfix

Previous version: V-051026 NDG - WebAudio update - PLEASE TEST

1. WebAudio reconfigured for less lags on mobile browsers
2. Small bugfixes in buffer and timing
3. Tried to implement an AudioWorklet/Ringpuffer like you might know from openwebrx

When you report, please include:
1. Sound card (or the output of: pactl list short sources)
2. The "[AUDIO-ROUTING] Karte: ..." line from the log
3. Browser + version, and whether audio stutters in the first seconds
4. The "Live:" and "net:" lines from Setup & Sync (screenshot is fine)
5. Background / screen-off: does the audio keep running?

Previous version:  V-041026 RMF *MILESTONE UPDATE*

1. New audio engine: smoother, lower latency, self-correcting. Rate and buffer settings are adjustable in "Setup & Sync."
2. New sound card detection: now works with most USB sound cards, not just C-Media devices.
3. S-SCAN / MW: waits 3 seconds after the signal ends before resuming the search. SCROLL speed is adjustable.
4. Key and control box support (optional; disabled by default): U/D = Channel, M = Mode, A = ASQ, S = Scan (long press = Scroll), F7/F8 = TX on/off.
5. Reduced data traffic for the waterfall display.
6. New installer (install.sh): starts automatically on boot; Mumble is now optional.

Note: Please update ae_5900_v2.py, index.html, and install.sh, then restart the program. You can find new configuration options in "Setup & Sync."

Previous version: V-300926 SWX

1. RX audio rebuilt; continues running in the background.
2. SCROLL function added to S-SCAN / MW (channel scanning with squelch open). To activate, press and hold the S-SCAN or MW button.

Note: Please take a look at the Setup & Sync section. There are new settings available, including for the waterfall.

Previous version: V-290926 AFX

1. Audio volume fix
Loud spikes upon connecting have been removed.

Note: Please take a look at the "Setup & Sync" section. There are new settings available there, including options for the waterfall display.

Previous version: V-271026 WBA

1. Waterfall adjusted
2. Bug fixes
3. WebAudio integrated via HTTPS/port 5443. The controls for WebAudio are located in the Setup & Sync section.

Note: Please take a look around the Setup & Sync area. There are new settings there, including some for the waterfall.

Previous version: V-251026 WFB

TESTING! I need to see for myself if I like this.

1. Fixed a "shaking" glitch in the desktop view.
2. Audio bars are now rendered with finer detail.
3. In Setup & Sync, you can choose between audio bars, a waterfall-like display, or both.

Previous version: V-241026 BGF

After a long, necessary hiatus, here are at least a few bug fixes.

1. S-Scan optimized.
2. Fixed errors in CLAR +/- UP/DOWN controls.
3. A/SQ Res. now provides visual feedback again.
4. UP/DOWN controls are now available in PA mode. This allows for blind adjustment of the physical device's volume if it is too quiet or too loud.

Previous version: V-200726 BTVO

1. S-meter via BT option
2. More stable VFO
3. CH50 bug fix

Previous version: V-090726 i3/a6 B-VFO

1. VFO Mode added.
2. Video tutorials added
3. Some bugfixes in UI

Previous version: V-050426 i1/a9 RIGC

1. hamctl/rigctl functions added.
   install dependencies (sudo apt install libhamlib-utils)

2. Openwebrx TX-Button is available in openwebrx_ptt_code.txt // copy/paste ready.
3. New install.sh added.

Previous version: V-300626 i4/a1 DSPx

1. Automatic adjustment to the display size between smartphone and computer.

Previous version: V-280626 i1/a1 BF

1. Bugfixes für V-240626

Previous version: V-240626 i1/a4 JS8

1. Reimplementation of JS8call control.
   
 As trigger in JS8call in Radio / Rigoptions (will switch on/off automatically) use:

```bash
curl -s http://127.0.0.1:5000/api/cmd/TX?state=%1
````
 In other digimodes use for TX:
  ```bash
  curl -s http://127.0.0.1:5000/api/cmd/TX?state=%1
````
 For RX:
 
   ```bash
    curl -s http://127.0.0.1:5000/api/cmd/TX?state=%0
   ````

Replace 127.0.0.1 with your ip.
You can also build a on/off script with these commands.

2. VOX bugfixes

Previous version: V-210626 i6/a9 BPLC

1. ALL country codes added. Greetings to my testers in Poland and Great Britain.
2. Again, some Bugfixes for FW 1.12 users.

Previous version: V-190626 i2/a5 CQRP

1. New terminal keys can be selected and edited in Setup & Sync.
2. Keys can be used to record and play back QSOs, as well as to record and repeat CQ calls. This function can be selected in Setup & Sync.
3. Bugfixes

Previous version: V-170626 i4/a1 FLK

1. Some bugfixes in UI.
2. A/SQ level to display added. Please first use A/SQ Res. (will run about 25sec) then use the A/SQ +/- buttons.
3. Ugly movement of buttons fixed.

Previous version: V-150626 i4/a5 BTN

1. Button bugfixes.

Previous version: V-120626 i1/a1 LN-RB

1. Roger beep switch added.

Previous version: V-110626 i9/a9 LNG

1. The language of the manual under Setup & Sync changes according to the browser language setting.

Previous version: V-110626 i8/a9 VX-RB-SM-MW

1. VOX function fixed.
2. Rogebeep function implemented.
3. Simulation mode added for testing without the box.
4. MultiWatch fixed.


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

Special thanks going out to all the referring sites i've seen these days:

- [blog.adafruit.com](https://blog.adafruit.com/2026/06/28/a-remote-web-rig-control-system-for-the-albrecht-ae-5900-radio-hamsunday/?__cf_chl_f_tk=ZeEFXVEeo3pQ0MyeQUiZ6NV9VGvb3nG0cls587OkBxI-1782807606-1.0.1.1-vs2hueUsJCEhc7sezrSgWTLAEHHWuS3q5fcnDK67Xqo)
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
