#include <Wire.h>
#include <TinyGPS++.h>
#include <WiFi.h>
#include <LiquidCrystal_I2C.h>

#define RXD2 16
#define TXD2 17
HardwareSerial neogps(1);

const char ssid[] = "JeepMobile";//"TIM-Salentu";//"RouterPi";//"TIM-03859326";
const char password[] = "@dQmBvxoNRiINTG@1LxZ5JshRz@";//"ScistiASantuVituETeStizzasti5724_@#";//"raspberry123";//"f5R235Dhc5bdYbCUtGfKH6zP";
unsigned long start;

// Create the lcd object address 0x3F and 16 columns x 2 rows 
LiquidCrystal_I2C lcd(0x27, 16,2);

TinyGPSPlus gps;


void WifiConnection(){
  WiFi.begin(ssid, password);
  
  lcd.setCursor(0,0);
  lcd.print("[WiFi] Connecting");
  
  
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    //Serial.print(".");
  }
  lcd.setCursor(0,1);
  lcd.print(WiFi.localIP());
  delay(5000);
  lcd.clear();
}

void setup() {
  lcd.begin();
  // Turn on the backlight on LCD. 
  lcd.backlight();

  //Serial.begin(115200);
  //Begin serial communication Arduino IDE (Serial Monitor)
  WifiConnection();
  //Begin serial communication Neo6mGPS
  neogps.begin(9600, SERIAL_8N1, RXD2, TXD2);

  start = millis();
}

float getGPS(int coord){
  boolean new_data = false;
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Retrieving");
  unsigned long start_while = millis();
  while (neogps.available() && start_while - millis() < 10000){
      if (gps.encode(neogps.read())){
        new_data = true;
        lcd.clear();
        lcd.print("Retrieving [OK]");
        break;
      }
      
    }
  /*lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(neogps.available());
  lcd.print(" ");
  lcd.print(gps.encode(neogps.read()));

  */
  boolean gps_encode = gps.encode(neogps.read());
  
  if(new_data == true){
    if(gps.location.isValid() == 1){
      lcd.clear();
      lcd.setCursor(0,0);
      lcd.print(gps.location.lat(),6);
      lcd.setCursor(0,1);
      lcd.print(gps.location.lng(),6);

      return coord == 0? gps.location.lat(): gps.location.lng();
    }
    else{
      lcd.setCursor(0,1);
      lcd.print("[PRINT] NO DATA");
    }
  }
  else{
    lcd.setCursor(0,1);
    lcd.print("[LOOP] NO DATA");    
  }

  return coord == 0? 44.083626: 12.534610;
}
void loop() {
  unsigned long end = millis();
  if(end - start >= 5000){
    start = end;
    getGPS(0);
  }
  //delay(5000);
}
