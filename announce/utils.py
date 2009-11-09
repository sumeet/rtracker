import struct
import socket
import binascii

def compact(ip, port, ascii=False):
	compacted = struct.pack('!4sH', socket.inet_aton(ip), port)
	return binascii.hexlify(compacted) if ascii else compacted
	
def expand(compacted):
	if len(compacted) == 12:
		compacted = binascii.unhexlify(compacted)
	ip,port = struct.unpack('!4sH', compacted)
	return (socket.inet_ntoa(ip), port)
	