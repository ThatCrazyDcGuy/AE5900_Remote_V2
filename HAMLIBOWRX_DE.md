#### Hamlib / Rigctl / OpenWebRX Setup

Zurück zur [README_DE](README_DE.md) · English: [HAMLIBOWRX.md](HAMLIBOWRX.md)

Das Programm bietet einen rigctl-kompatiblen Server auf **Port 4532** des Raspberry Pi an (`rigctl -m 2 -r IP-DES-RASPBERRY:4532`). Damit sprechen flrig, fldigi, grig, JS8Call, WSJT-CB und OpenWebRX. Moduswechsel von dort beachten die Einstellungen Skip PA / Skip CW im Setup & Sync.

- Tutorial AE5900_REMOTE_V2: VFO am Gerät und in der WebUI aktivieren.

[![AE5900 Webinterface V2 ](https://img.youtube.com/vi/Qk8EmSfFJvY/0.jpg)](https://www.youtube.com/watch?v=Qk8EmSfFJvY)

- Tutorial AE5900_REMOTE_V2: OpenWebRX zur Steuerung des AE5900 einrichten und verwenden

[![AE5900 Webinterface V2 ](https://img.youtube.com/vi/0zt2-Wdh3UA/0.jpg)](https://www.youtube.com/watch?v=0zt2-Wdh3UA)

**1. PTT-Taste in OpenWebRX**

In den OpenWebRX-Einstellungen unter *settings/general* das Feld *Photo description* bearbeiten und den folgenden Code einfügen. Trage bei `ALBRECHT_HOST` den Hostnamen oder die IP-Adresse deines Raspberry Pi ein:

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

**2. Rig-Steuerung in OpenWebRX**

In *settings/reporting* die RigControl-Einstellungen eintragen:

![AE5900_Remote_v2](/pictures/owrx2.png)

**3. Profil**

In *settings/sdr* die Profil-Einstellungen eintragen:

![AE5900_Remote_v2](/pictures/owrx3.png)

**4. Optional: OpenWebRX als S-Meter**

Dein OpenWebRX kann dem AE5900 auch als S-Meter dienen. Siehe [SMETER_DE.md](SMETER_DE.md).
