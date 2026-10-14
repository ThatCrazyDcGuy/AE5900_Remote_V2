### S-Meter: choose your source

Back to the [README](README.md) · Deutsch: [SMETER_DE.md](SMETER_DE.md)

The AE-5900 only shows its S-meter on the device. For the web interface there are three sources. Choose one in **Setup & Sync → S-Meter source**:

| Source | What you need | Notes |
|---|---|---|
| Hardware mod (ESP32) | Opened radio, ESP32 | Bluetooth, see [BTSMETER.md](BTSMETER.md). This is the default. |
| SDR dongle (RTL-SDR) | RTL-SDR dongle with its own antenna, package `rtl-sdr` | Measures the power of the current channel. |
| OpenWebRX (local) | Your own, private OpenWebRX server | Reads the S-meter value of an additional OpenWebRX client. |
| Off | - | No S-meter. |

During transmit the S-meter shows 0 (this is also true for the ESP32 mod).

#### Calibration (SDR and OpenWebRX)

Every source reports a level in dB. You tell the program which value is 0 % and which is 100 %:

1. **Floor (0 %)**: Tune to a quiet channel and press **= now** next to *Floor*.
2. **Full (100 %)**: When a strong station is on the channel, press **= now** next to *Full*.
3. **Smoothing**: Low values give a calm needle, 1 switches smoothing off.

The status line below shows the live dB value. Defaults: SDR -60 dB / -20 dB, OpenWebRX -85 dB / -30 dB. Every installation is different, so expect to adjust them.

#### Using an RTL-SDR dongle

```bash
sudo apt install rtl-sdr
```

- Use a dongle (and ideally an antenna) that **nothing else** uses at the same time, for example not your OpenWebRX.
- If the dongle is not found, the DVB driver may have grabbed it. Blacklist it once and reboot:

```bash
echo "blacklist dvb_usb_rtl28xxu" | sudo tee /etc/modprobe.d/blacklist-rtl.conf
```

- *SDR gain* is a number in dB or `auto`. Start with 30 and adjust.

#### Using OpenWebRX as the S-meter

- Use your **own, private** OpenWebRX server (not a public one). The program connects as an additional client and follows the channel and mode of the radio.
- Enter its address in *OpenWebRX address* (default `127.0.0.1:8073`).
- OpenWebRX does not have to be stopped for this.
- Use only one person on that server at a time.
