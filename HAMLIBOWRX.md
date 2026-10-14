#### Hamlib / Rigctl / OpenWebRX Setup

Back to the [README](README.md) · Deutsch: [HAMLIBOWRX_DE.md](HAMLIBOWRX_DE.md)

The program offers a rigctl-compatible server on **port 4532** of the Raspberry Pi (`rigctl -m 2 -r IP-OF-YOUR-PI:4532`). flrig, fldigi, grig, JS8Call, WSJT-CB and OpenWebRX talk to it. Mode changes from those programs respect the Skip PA / Skip CW settings in Setup & Sync.

- Tutorial AE5900_REMOTE_V2: Activate the VFO on the device and in the WebUI.

[![AE5900 Web Interface V2](https://img.youtube.com/vi/Qk8EmSfFJvY/0.jpg)](https://www.youtube.com/watch?v=Qk8EmSfFJvY)

- Tutorial AE5900_REMOTE_V2: Set up and use OpenWebRX to control the AE5900.

[![AE5900 Web Interface V2](https://img.youtube.com/vi/0zt2-Wdh3UA/0.jpg)](https://www.youtube.com/watch?v=0zt2-Wdh3UA)

**1. PTT button in OpenWebRX**

In the OpenWebRX settings under *settings/general*, edit the *Photo description* field and paste the code below. Enter the hostname or IP address of your Raspberry Pi at `ALBRECHT_HOST`:

```html
<script type="text/javascript">
// === CONFIGURATION ===
// Enter the hostname or IP address of your Albrecht Pi below, after ALBRECHT_HOST = (e.g. 'ae5900ctrl' or '192.168.122.50')
var ALBRECHT_HOST = '127.0.0.1';
// =====================

if (document.getElementsByTagName('a')[0]) {
    document.getElementsByTagName('a')[0].innerHTML = '';
}

if (typeof window.owrxPttState === 'undefined') {
    window.owrxPttState = false;
}

if (!document.getElementById('owrx-cat-ptt')) {
    var pttBtn = document.createElement('button');
    pttBtn.id = 'owrx-cat-ptt';
    pttBtn.innerHTML = 'RX/TX';

    pttBtn.style.background = '#ADD8E6';
    pttBtn.style.color = '#fff';
    pttBtn.style.border = '1px solid #ff3333';
    pttBtn.style.padding = '5px 15px';
    pttBtn.style.marginLeft = '15px';
    pttBtn.style.cursor = 'pointer';
    pttBtn.style.fontWeight = 'bold';
    pttBtn.style.borderRadius = '4px';
    pttBtn.style.fontFamily = 'monospace';

    pttBtn.onclick = function() {
        window.owrxPttState = !window.owrxPttState;
        var pttVal = window.owrxPttState ? '1' : '0';

        fetch('http://' + ALBRECHT_HOST + ':5000/api/rig/ptt/' + pttVal, { mode: 'cors' })
            .then(function(r) { return r.text(); })
            .then(function(text) {
                if (window.owrxPttState) {
                    pttBtn.style.background = '#ff0000';
                    pttBtn.style.boxShadow = '0 0 10px red';
                    pttBtn.innerHTML = ' T X ';
                } else {
                    pttBtn.style.background = '#008000';
                    pttBtn.style.boxShadow = 'none';
                    pttBtn.innerHTML = ' R X ';
                }
            })
            .catch(function(err) {
                console.error('Albrecht API not reachable:', err);
                window.owrxPttState = !window.owrxPttState; // Reset on err
                pttBtn.innerHTML = 'API ERR';
            });
    };

    var firstLink = document.getElementsByTagName('a')[0];
    if (firstLink && firstLink.parentNode) {
        firstLink.parentNode.appendChild(pttBtn);
    }
}
</script>
```

![AE5900_Remote_v2](/pictures/owrx1.png)

**2. Rig control in OpenWebRX**

Enter the RigControl settings under *settings/reporting*:

![AE5900_Remote_v2](/pictures/owrx2.png)

**3. Profile**

Enter the profile settings under *settings/sdr*:

![AE5900_Remote_v2](/pictures/owrx3.png)

**4. Optional: OpenWebRX as S-meter**

Your OpenWebRX can also serve as the S-meter of the AE5900. See [SMETER.md](SMETER.md).
