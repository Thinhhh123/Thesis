import serial
import time

# Initialize global variables
temperature = None
humidity = None
pressure = None
current = None
voltage = None

def update_sensor_values(data_str):
    global temperature, humidity, pressure, current, voltage
    # Assuming data_str is already the list containing your sensor values
    if len(data_str) >= 5:  # Ensure there are at least 5 elements
        temperature = float(data_str[0])
        humidity = float(data_str[1])
        pressure = float(data_str[2])
        current = float(data_str[3])
        voltage = float(data_str[4])
        # Now, these global variables are updated

def print_sensor_values():
    # Use global keyword if you need to modify global variables inside this function, else it's optional
    print(f"Temperature: {temperature} °C, Humidity: {humidity} %, Pressure: {pressure} hPa, Current: -{current} mA, Voltage: {voltage} V\n")

arSerial = serial.Serial('/dev/ttyACM0', 115200)
time.sleep(1)

try:
    while True:
        if arSerial.in_waiting > 0:
            data_str = arSerial.readline().decode('utf-8').strip().split(',')
            print(f"Raw data: {data_str}")  # For debugging purposes

            update_sensor_values(data_str)
            print_sensor_values()

except KeyboardInterrupt:
    print("Program has stopped !")
finally:
    arSerial.close()  # Ensure serial connection is closed when the program ends or an error occurs
