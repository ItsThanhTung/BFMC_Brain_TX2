# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

from imuHandler import IMUHandler
import matplotlib.pyplot as plt
import signal
import sys
from time import sleep
import numpy as np
def exit_handler(signum, frame):
	IMU.stop()
	IMU.join()
	np.save('yaw.npy',yaw_arr)
	sys.exit(0)
yaw_arr=[]
def main():
	global IMU
	signal.signal(signal.SIGINT, exit_handler)
	IMU = IMUHandler()
	IMU.start()
	sleep(1)
	IMU.set_yaw()
 
	while True:
		delta_yaw = IMU.get_yaw()
		yaw_arr.append(delta_yaw)
		print(delta_yaw)
		sleep(0.01)
	# IMU.stop()
if __name__ == "__main__":
	main()


