// Rally Tripmaster V0.1 – experimental firmware, ESP32-S3-MINI-1
// Important: 10 Hz GNSS output is not configured here. Configure MAX-M10N
// with u-center (NMEA RMC at 10 Hz) and 115200 baud BEFORE use.
// Uses GNSS speed-over-ground integration, not raw position deltas.
#include <Arduino.h>
#include <Preferences.h>
#include <TinyGPSPlus.h>
#include <U8g2lib.h>

static constexpr int PIN_MODE=1, PIN_PLUS=2, PIN_MINUS=4, PIN_RESET=5, PIN_LIGHT=6;
static constexpr int PIN_BL=7, PIN_LCD_RST=8, PIN_LCD_A0=9, PIN_LCD_CS=10;
static constexpr int PIN_LCD_MOSI=11, PIN_LCD_SCLK=12;
static constexpr int PIN_GNSS_RX=17, PIN_GNSS_TX=18;

HardwareSerial gnssSerial(1);
TinyGPSPlus gps;
Preferences store;
// DOGL128 is an ST7565 display. Software SPI avoids board-specific SPI host problems.
U8G2_ST7565_EA_DOGM128_F_4W_SW_SPI lcd(U8G2_R0, PIN_LCD_SCLK,
  PIN_LCD_MOSI, PIN_LCD_CS, PIN_LCD_A0, PIN_LCD_RST);

static double odoMeters=0.0, tripMeters=0.0;
static double previousSpeedMS=0.0;
static uint32_t previousGNSSms=0, lastGoodFixms=0, lastDrawms=0, lastPersistms=0;
static bool previousSpeedReady=false;
static double lastSpeedKmh=0.0;
static uint8_t brightnessIndex=2;
static const uint8_t brightness[4]={0,24,76,180};
static bool tripView=true;

struct Key {
  uint8_t pin;
  bool rawPressed=false, stablePressed=false, heldAction=false;
  uint32_t changedMs=0, pressedMs=0;
};
static Key keys[5]={{PIN_MODE},{PIN_PLUS},{PIN_MINUS},{PIN_RESET},{PIN_LIGHT}};

static void backlight() { analogWrite(PIN_BL, brightness[brightnessIndex]); }

static void saveCounters() {
  // Flash wear: this is NOT an interruption-proof store. FRAM hardware remains optional.
  store.putDouble("total_m",odoMeters);
  store.putDouble("trip_m",tripMeters);
  lastPersistms=millis();
}

static void pressKey(int index) {
  switch(index) {
    case 0: tripView=!tripView; break;
    case 1: tripMeters+=10.0; saveCounters(); break;
    case 2: tripMeters=fmax(0.0,tripMeters-10.0); saveCounters(); break;
    case 3: /* RESET requires 2 s hold */ break;
    case 4: brightnessIndex=(brightnessIndex+1)%4; backlight(); break;
  }
}

static void processButtons() {
  const uint32_t now=millis();
  for(int i=0;i<5;i++) {
    Key &k=keys[i];
    const bool raw=digitalRead(k.pin)==LOW;
    if(raw!=k.rawPressed) {k.rawPressed=raw; k.changedMs=now;}
    if(now-k.changedMs>=35 && k.stablePressed!=k.rawPressed) {
      k.stablePressed=k.rawPressed;
      if(k.stablePressed) {k.pressedMs=now;k.heldAction=false; if(i!=3) pressKey(i);}
    }
    if(i==3 && k.stablePressed && !k.heldAction && (now-k.pressedMs>2000)) {
      tripMeters=0; k.heldAction=true; saveCounters();
    }
  }
}

static void processGNSS() {
  while(gnssSerial.available()) gps.encode(gnssSerial.read());
  // TinyGPSPlus speed.isUpdated() is cleared when its value is retrieved.
  if(!gps.speed.isUpdated()) return;
  const double kmh=gps.speed.kmph();
  const uint32_t now=millis();
  bool valid = gps.location.isValid() && gps.location.age()<1500 &&
               gps.satellites.isValid() && gps.satellites.value()>=4 &&
               kmh>=0.0 && kmh<230.0;
  if(gps.hdop.isValid() && gps.hdop.hdop()>4.0) valid=false;
  if(!valid) { previousSpeedReady=false; return; }
  lastGoodFixms=now;
  // Below 0.7 km/h treat Doppler noise as zero; bench-verify this threshold.
  const double speedMS=kmh<0.7 ? 0.0 : (kmh/3.6);
  if(previousSpeedReady) {
    const double dt=(now-previousGNSSms)/1000.0;
    // No dead reckoning during dropout: do NOT bridge gaps beyond 350 ms.
    // For 1-Hz GNSS change dt limit to e.g. 1.3 s (less accurate).
    if(dt>0.03 && dt<=0.35) {
      const double ds=(previousSpeedMS+speedMS)*0.5*dt;
      odoMeters+=ds; tripMeters+=ds;
    }
  }
  previousGNSSms=now;
  previousSpeedMS=speedMS;
  previousSpeedReady=true;
  lastSpeedKmh=kmh;
}

static void draw() {
  char line[26];
  lcd.clearBuffer();
  lcd.setFont(u8g2_font_5x7_tf);
  bool hasFix = (millis()-lastGoodFixms)<1500 && previousSpeedReady;
  lcd.drawStr(0,7,tripView ? "TRIPMASTER  TRIP" : "TRIPMASTER  TOTAL");
  lcd.drawStr(105,7,hasFix ? "GPS" : "---");
  double mainKm=(tripView?tripMeters:odoMeters)/1000.0;
  snprintf(line,sizeof(line),"%07.3f",mainKm);
  lcd.setFont(u8g2_font_logisoso20_tn);
  lcd.drawStr(1,29,line);
  lcd.drawHLine(0,34,128);
  lcd.setFont(u8g2_font_5x7_tf);
  lcd.drawStr(0,42,tripView ? "TOTAL km" : "TRIP km");
  lcd.drawStr(91,42,"KM/H");
  snprintf(line,sizeof(line),"%07.3f",(tripView?odoMeters:tripMeters)/1000.0);
  lcd.setFont(u8g2_font_helvB12_tn);
  lcd.drawStr(0,62,line);
  if(hasFix) snprintf(line,sizeof(line),"%.0f",lastSpeedKmh);
  else strcpy(line,"--");
  lcd.drawStr(94,62,line);
  lcd.sendBuffer();
}

void setup() {
  Serial.begin(115200);
  for(auto &k:keys) pinMode(k.pin,INPUT_PULLUP);
  pinMode(PIN_BL,OUTPUT);backlight();
  store.begin("tripmaster",false);
  odoMeters=store.getDouble("total_m",0.0);
  tripMeters=store.getDouble("trip_m",0.0);
  // MAX-M10N must be configured to the same baud and 10 Hz RMC output.
  gnssSerial.begin(115200,SERIAL_8N1,PIN_GNSS_RX,PIN_GNSS_TX);
  lcd.begin();
  lcd.setContrast(145); // bench-calibrate for the real LCD and viewing angle
  lastPersistms=millis();
}
void loop() {
  processGNSS();
  processButtons();
  if(millis()-lastDrawms>=100) {draw();lastDrawms=millis();}
  if(millis()-lastPersistms>=30000) saveCounters();
  delay(1);
}
