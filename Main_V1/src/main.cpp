#include <Arduino.h>
#include <Adafruit_INA219.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME280 bme; // I2C
Adafruit_INA219 ina219;
Adafruit_SSD1306 display = Adafruit_SSD1306(128, 32, &Wire);

unsigned long Time;
float shuntvoltage, busvoltage, current_mA, power_mW, loadvoltage;
float temp, press, humi, altitude;
String data_ = "";
const int buttonPin = 10;  // the number of the pushbutton pin
const int ledPin = 11;    // the number of the LED pin
int buttonState = 0;

void setup() 
{
  Serial.begin(115200);

  // initialize the LED pin as an output:
  pinMode(ledPin, OUTPUT);
  // initialize the pushbutton pin as an input:
  pinMode(buttonPin, INPUT_PULLUP);

  Serial.println(F("BME280 test"));
  
  
  //Init Oled
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);  
  display.display();
  delay(100);
  display.clearDisplay();
  display.display();
  display.setTextSize(1);
  display.setTextColor(WHITE);

  // Initialize the INA219.
  if (!ina219.begin()) {
    Serial.println("Failed to find INA219 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("Measuring voltage, current, and power with INA219 ...");
  
  //Init BME280
  bool status;
  status = bme.begin(0x76);  
  if (!status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    while (1);
  }
  Serial.println("-- Default Test --");

  Time = millis();
  Serial.println();
}

void loop()
 { 
  if((unsigned long)(millis() - Time) > 1000)
  {
    display.setCursor(0,0);
    display.clearDisplay();

    // BME Sensor
    temp = bme.readTemperature();
    press = bme.readPressure() / 100.0F;
    humi = bme.readHumidity();

    // Ina219 curernt sensor
    shuntvoltage = ina219.getShuntVoltage_mV();
    busvoltage = ina219.getBusVoltage_V();
    current_mA = ina219.getCurrent_mA();
    power_mW = ina219.getPower_mW();
    loadvoltage = busvoltage + (shuntvoltage / 1000);

    //Save and send data to Raspberry Pi
    // Send data to Rasp
    data_ = String(temp) + String(',') +  String(humi) + String(',') + String(press) + String(',') + String(current_mA) + String(',') + String(loadvoltage);
    Serial.println("Data frame: temp,humi.press,current,voltage");
    Serial.println("Data : " + data_);

    
    // Test data from Serial monitor: uncomment when send data to Rasp
    Serial.print("Temperature = "); Serial.print(temp); Serial.println(" *C");
    Serial.print("Humidity = "); Serial.print(humi); Serial.println(" %");
    Serial.print("current_mA = "); Serial.print(current_mA); Serial.println(" mA");
    Serial.print("busvoltage = "); Serial.print(busvoltage); Serial.println(" V");

    // Oled dislay
    display.print("Temperature: "); display.print(temp); display.println(" *C");
    display.print("Humidity: "); display.print(humi); display.println(" %");
    display.print("current_mA: "); display.print(current_mA); display.println(" mA");
    display.print("busvoltage: "); display.print(busvoltage); display.println(" V");


    Serial.println();
    display.display();

    Time = millis();
  }


  buttonState = digitalRead(buttonPin);
  if (buttonState == HIGH) {
    digitalWrite(ledPin, LOW);
  } else {
    digitalWrite(ledPin, HIGH);
  }

}