import serial
import time
import requests  # Import thư viện requests

# Khai báo API Key và URL
THINGSPEAK_WRITE_API_KEY = 'FUOW0FUI40SSBDMS'
THINGSPEAK_CHANNEL_UPDATE_URL = 'https://api.thingspeak.com/update'

# Thiết lập thời gian chờ (ví dụ: 5 giây hoặc 10 giây)
SEND_INTERVAL = 10  # Thời gian gửi lại dữ liệu (tính bằng giây)

def send_to_thingspeak(temperature, humidity, pressure, current, voltage):
    data = {
        'api_key': THINGSPEAK_WRITE_API_KEY,
        'field1': temperature,
        'field2': humidity,
        'field3': pressure,
        'field4': current,
        'field5': voltage
    }
    try:
        response = requests.get(THINGSPEAK_CHANNEL_UPDATE_URL, params=data)
        print(f"Data sent to ThingSpeak with response: {response.text}")
    except Exception as e:
        print(f"Failed to send data to ThingSpeak: {e}")

arSerial = serial.Serial('/dev/ttyACM0', 115200)
time.sleep(1)

# Khởi tạo biến để theo dõi thời gian cuối cùng dữ liệu được gửi
last_sent_time = time.time()

try:
    while True:
        current_time = time.time()
        if arSerial.in_waiting > 0:
            data_str = arSerial.readline().decode('utf-8').strip().split(',')
            if len(data_str) >= 5:
                temperature = float(data_str[0])
                humidity = float(data_str[1])
                pressure = float(data_str[2])
                current = float(data_str[3])
                voltage = float(data_str[4])
                print(f"Temperature: {temperature} °C, Humidity: {humidity} %, Pressure: {pressure} hPa, Current: {current} mA, Voltage: {voltage} V\n")

                # Kiểm tra nếu thời gian hiện tại - thời gian gửi cuối cùng >= khoảng thời gian cần chờ
                if (current_time - last_sent_time) >= SEND_INTERVAL:
                    send_to_thingspeak(temperature, humidity, pressure, current, voltage)
                    last_sent_time = current_time  # Cập nhật thời gian gửi cuối cùng
except KeyboardInterrupt:
    print("Program has stopped !")
finally:
    arSerial.close()
