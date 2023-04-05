import serial
import time

ser = serial.Serial("/dev/ttyACM0", 115200)

prev = time.time()
command_msg = "#5:1;:6c;;\r\n"
print("Start")
ser.write(command_msg.encode('ascii'))
# print("Send time ", time.time()-prev)
prev = time.time()
rcv1 = ser.readline()
rcv2 = ser.readline()
# rcv3 = ser.readline()
end = time.time() - prev
print("Read + Write Time ", time.time() - prev)
print("Rcv Data rcv ", rcv1, rcv2 )