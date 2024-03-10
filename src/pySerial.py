import serial
import time

arSerial = serial.Serial('/dev/ttyACM0', 115200)
time.sleep(1)

try:
    while True:
        if arSerial.in_waiting > 0:
            data_str = arSerial.readline().decode('utf-8').strip().split(',')
            print(f"Raw data: {data_str}")  # In ra dữ liệu thô để kiểm tra

            if len(data_str) == 4:
                try:
                    temp = float(data_str[0])
                    humidity = float(data_str[1])
                    pressure = float(data_str[2])
                    current = float(data_str[3])
                    
                    # In ra các giá trị
                    print(f"Temperature: {temp} °C")
                    print(f"Humidity: {humidity} %")
                    print(f"Pressure: {pressure} hPa")
                    print(f"Current: {current} A")
                except ValueError as e:
                    print(f"Error converting data: {e}")
            else:
                print("Received incomplete data.")
except KeyboardInterrupt:
    print("Program has stopped !")
finally:
    arSerial.close()  # Đảm bảo đóng kết nối serial khi kết thúc chương trình hoặc khi có lỗi
