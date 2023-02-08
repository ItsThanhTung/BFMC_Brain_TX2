import crc8 

str= '10.2;'
hash = crc8.crc8()
hash.update(str.encode('ascii'))

print(hash.hexdigest())