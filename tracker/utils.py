import struct
import socket
import binascii
import hunnyb
from werkzeug import Response
import db

def compact(ip, port, ascii=False):
	compacted = struct.pack('!4sH', socket.inet_aton(ip), port)
	return binascii.hexlify(compacted) if ascii else compacted
	
def expand(compacted):
	if len(compacted) == 12:
		compacted = binascii.unhexlify(compacted)
	ip,port = struct.unpack('!4sH', compacted)
	return (socket.inet_ntoa(ip), port)
	
class bResponse(Response):
	def __init__(self, data):
		super(bResponse, self).__init__(hunnyb.encode(data), mimetype='text/plain')
		
def scrapedict(torrent):
	return {
		torrent.binary_hash(): {
			'complete': len(torrent.find_peers(status='seed')),
			'downloaded': torrent.completed(),
			'incomplete': len(torrent.find_peers(status='leech')),
		},
	}
	
def get_torrents(self):
	return [db.Torrent(key.lstrip('!')) for key in db.client.keys('!*')]