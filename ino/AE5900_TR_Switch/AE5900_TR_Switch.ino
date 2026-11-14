/*
  AE5900 T/R switch  -  ESP32-C3 Super Mini
  -----------------------------------------
  Switches the relay that grounds the SDR branch while the AE-5900 transmits.

  Relay logic (fail-safe):
    relay OFF (coil without current) = SDR input GROUNDED  = "TX" / safe position
    relay ON  (coil energised)       = SDR connected       = "RX"
  So: power failure, crash, USB unplugged or no heartbeat from the Raspberry Pi
  always ends in the grounded (safe) position.

  Serial protocol over USB (115200, text lines, \n terminated):
    Pi -> ESP:  PING   -> PONG AE5900-TR <version> <state>
                HB     -> HB <state>            (heartbeat, every ~1 s)
                RX     -> OK RX                 (relay on,  SDR connected)
                TX     -> OK TX                 (relay off, SDR grounded)
                ST     -> ST <state>
    ESP -> Pi:  EV WD  (watchdog: no heartbeat, relay went to the safe position)
    <state> is RX or TX.

  Arduino IDE settings:
    Board: "ESP32C3 Dev Module"
    USB CDC On Boot: "Enabled"      <- important, otherwise Serial does not appear on USB
    Everything else default.

  Wiring (relay driver):
    GPIO4 --[1k]--> base BC337 (or 2N2222), emitter to GND,
    10k from base to GND (keeps the relay off while the ESP boots),
    relay coil between 5V and the collector, 1N4148/1N4007 across the coil
    (cathode to 5V, anode to the collector).
*/

#define FW_VERSION   "1"
#define PIN_RELAY    4        // to the transistor base (via 1k)
#define PIN_LED      8        // onboard LED of the Super Mini (active LOW)
#define WD_MS        3000UL   // no line from the Pi for this long -> safe position

bool rxState = false;         // true = relay energised = SDR connected
unsigned long lastRx = 0;
String line;

void setRelay(bool rx) {
  rxState = rx;
  digitalWrite(PIN_RELAY, rx ? HIGH : LOW);
  digitalWrite(PIN_LED, rx ? LOW : HIGH);   // LED on = RX (SDR connected)
}

const char* stateName() { return rxState ? "RX" : "TX"; }

void handleLine(String s) {
  s.trim();
  s.toUpperCase();
  if (s.length() == 0) return;
  lastRx = millis();
  if (s == "PING") {
    Serial.print("PONG AE5900-TR "); Serial.print(FW_VERSION); Serial.print(" "); Serial.println(stateName());
  } else if (s == "HB") {
    Serial.print("HB "); Serial.println(stateName());
  } else if (s == "RX") {
    setRelay(true);
    Serial.println("OK RX");
  } else if (s == "TX") {
    setRelay(false);
    Serial.println("OK TX");
  } else if (s == "ST") {
    Serial.print("ST "); Serial.println(stateName());
  } else {
    Serial.println("ERR");
  }
}

void setup() {
  pinMode(PIN_RELAY, OUTPUT);
  pinMode(PIN_LED, OUTPUT);
  setRelay(false);                 // always start in the safe position
  Serial.begin(115200);
#if defined(ESP_ARDUINO_VERSION_MAJOR) && ESP_ARDUINO_VERSION_MAJOR >= 3
  Serial.setTxTimeoutMs(0);        // never block when nobody listens on USB
#endif
  lastRx = millis();
}

void loop() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (line.length()) { handleLine(line); line = ""; }
    } else if (line.length() < 32) {
      line += c;
    } else {
      line = "";                   // garbage, start over
    }
  }
  // Watchdog: the Pi sends HB every second. Without it, go to the safe position.
  if (rxState && (millis() - lastRx > WD_MS)) {
    setRelay(false);
    Serial.println("EV WD");
  }
}
