### The Bluetooth S-Meter part // Device mod required

Back to the [README](README.md) · Deutsch: [BTSMETER_DE.md](BTSMETER_DE.md)

I was able to find the pinout for the external S-meter.
Instead of using a different cable/output/connector I decided to use an ESP32 Wroom and now we have an S-meter over BT.

Let's take a look at some photos and screenshots here:

![AE5900_Remote_v2](/pictures/bt-smeter.png)

![AE5900_Remote_v2](/pictures/bt-arduino.png)

![AE5900_Remote_v2](/pictures/bt-esp32device.png)

![AE5900_Remote_v2](/pictures/bt-soldering0.png)

![AE5900_Remote_v2](/pictures/bt-soldering1.png)

![AE5900_Remote_v2](/pictures/bt-soldering2.png)

The code is available in the `ino` folder.

Pair the device with your Raspberry Pi/host using `bluetoothctl` (pair, trust, connect).

Run this once (use your own MAC address):

```bash
sudo rfcomm bind rfcomm0 EC:E3:34:46:D8:7E
```

```bash
echo "$USER ALL=(ALL) NOPASSWD: /usr/bin/rfcomm" | sudo tee /etc/sudoers.d/ae5900_rfcomm && sudo chmod 0440 /etc/sudoers.d/ae5900_rfcomm
```

Then, in Setup & Sync under *S-Meter source*, choose "Hardware mod (ESP32)" (the default) and enter the MAC address in *Bluetooth S-Meter MAC*. More about the sources: [SMETER.md](SMETER.md).

Have fun!
