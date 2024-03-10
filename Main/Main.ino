#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_BME280.h>
#include <Adafruit_INA219.h>

#define SEALEVELPRESSURE_HPA (1013.25)
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
Adafruit_BME280 bme;
Adafruit_INA219 ina219;

unsigned long Time;
bool readINA219 = true; // Đặt cờ này thành false nếu bạn không muốn đọc INA219

void setup() {
  Serial.begin(115200);
  Wire.begin();
  while (!Serial) delay(10);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }
  delay(500);
  display.clearDisplay();
  display.setTextColor(WHITE);
  Serial.println("-- System Test --");

  Serial.println(F("BME280 test"));
  if (!bme.begin(0x76)) {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    while (1);
  }

  Time = millis();
}

float shuntvoltage = ina219.getShuntVoltage_mV();
float busvoltage = ina219.getBusVoltage_V();
float current_mA = ina219.getCurrent_mA();
float power_mW = ina219.getPower_mW();
float loadvoltage = busvoltage + (shuntvoltage / 1000);

void loop() {
  if ((unsigned long)(millis() - Time) >= 1000) {
    float temp = bme.readTemperature();
    float press = bme.readPressure() / 100.0F;
    float humi = bme.readHumidity();
    float altitude = bme.readAltitude(SEALEVELPRESSURE_HPA);


    //LCD display update
    display.clearDisplay();
    // Hiển thị nhiệt độ, độ ẩm...

    if (readINA219 && ina219.begin()) 
    {
      Serial.println("INA219 chip start");
      float shuntvoltage = ina219.getShuntVoltage_mV();
      float busvoltage = ina219.getBusVoltage_V();
      float current_mA = ina219.getCurrent_mA();
      float power_mW = ina219.getPower_mW();
      float loadvoltage = busvoltage + (shuntvoltage / 1000);

      // Hiển thị dòng điện, điện áp...
      // display Current, Voltage
    display.setTextSize(1);
    display.setCursor(0, 30);
    display.print("I:");
    display.setTextSize(1);
    display.setCursor(30, 30);
    display.print(current_mA);
    display.print(" A");

    // display Current, Voltage
    display.setTextSize(1);
    display.setCursor(0, 40);
    display.print("V:");
    display.setTextSize(1);
    display.setCursor(30, 40);
    display.print(busvoltage);
    display.print(" V");

    Serial.print("Temperature = ");
    Serial.print(temp);
    Serial.print(" *C\t");
    Serial.print("Pressure = ");
    Serial.print(press);
    Serial.print(" hPa\t");

    Serial.print("Approx. Altitude = ");
    Serial.print(altitude);
    Serial.print(" m\t");
    Serial.print("Humidity = ");
    Serial.print(humi);
    Serial.print(" %\t");

    Serial.print("current_mA = ");
    Serial.print(current_mA);
    Serial.println(" A");

    } else {
      Serial.println("INA219 read skipped");
    }

    display.display();
    Time = millis();
  }
}
