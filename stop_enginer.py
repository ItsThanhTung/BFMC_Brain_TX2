import serial
import time
ser = serial.Serial("/dev/ttyACM0", 115200)


cmd = b"#1:0.0;;\r\n"
ang0 = b"#2:0;;\r\n"
# cmd2 = b"#1:0.3;;\r\n"
# print("cmd ", cmd)
ser.write(cmd)
time.sleep(0.1)
ser.write(cmd)
time.sleep(0.1)
ser.write(ang0)
time.sleep(0.1)
ser.write(ang0)
time.sleep(0.1)
