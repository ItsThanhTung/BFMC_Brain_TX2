from smbus2 import SMBus


bus = SMBus(0)
data = bus.read_byte_data(0x29,0x34)
print("Data ", data)
bus.close()