import time
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055

from smbus2 import SMBus

# bus = SMBus(0)
# data = bus.read_byte_data(0x29,0x34)
# print("Data ", data)
# bus.close()

i2c = I2C(0)  # Device is /dev/i2c-1
print("Not init")
time.sleep(1)
sensor = adafruit_bno055.BNO055_I2C(i2c,0x29)
# sensor.
# i2c.deinit()
print("Inited")
last_val = 0xFFFF

iscalib = sensor.calibrated

if(iscalib):
    print("Calibrated")

# while True:
#     pass

def temperature():
    global last_val  # pylint: disable=global-statement
    result = sensor.temperature
    if abs(result - last_val) == 128:
        result = sensor.temperature
        if abs(result - last_val) == 128:
            return 0b00111111 & result
    last_val = result
    return result


while True:
    # print("Accelerometer (m/s^2): {}".format(sensor.acceleration))
    # print("Gyroscope (rad/sec): {}".format(sensor.gyro))
    # print("Linear acceleration (m/s^2): {}".format(sensor.linear_acceleration))
    print("Euler angle: {}".format(sensor.euler))
    
    print("Quaternion: {}".format(sensor.quaternion))
    time.sleep(0.2)
    