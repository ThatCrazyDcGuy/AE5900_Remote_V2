#### Hamlib / Rigctl / Openwebrx setup

- Tutorial AE5900_REMOTE_V2: VFO am Gerät und in der WebUI aktivieren.

[![AE5900 Webinterface V2 ](https://img.youtube.com/vi/Qk8EmSfFJvY/0.jpg)](https://www.youtube.com/watch?v=Qk8EmSfFJvY)

- Tutorial AE5900_REMOTE_V2: OpenWebRX zur Steuerung des AE5900 einrichten und verwenden

[![AE5900 Webinterface V2 ](https://img.youtube.com/vi/0zt2-Wdh3UA/0.jpg)](https://www.youtube.com/watch?v=0zt2-Wdh3UA)

- PTT-Code in den OpenWebRX-Einstellungen unter „Allgemein“ im Feld „Bildbeschreibung bearbeiten“ (Hostname/IP-Adresse) hinzufügen.

- settings/general in Photo description bearbeiten (Hostname/IP-Adresse) und Folgendes hinzufügen:

```bash
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
                console.error('Albrecht API nicht erreichbar:', err);
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
````
![AE5900_Remote_v2](/pictures/owrx1.png)

- settings/reporting in RigControl settings hinzufügen:

![AE5900_Remote_v2](/pictures/owrx2.png)

- settings/sdr in Profile settings hinzufügen:

![AE5900_Remote_v2](/pictures/owrx3.png)
