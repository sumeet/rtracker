import struct
import socket
import binascii
from bzrlib import bencode
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
	"""
	Response object used to convert content value into a bencoded dictionary.
	"""
	def __init__(self, data):
		super(bResponse, self).__init__(bencode.bencode(data), mimetype='text/plain')
		
def scrapedict(torrent):
	return {
		torrent.binary_hash(): {
			'complete': len(torrent.find_peers(status='seed')),
			'downloaded': torrent.completed(),
			'incomplete': len(torrent.find_peers(status='leech')),
		},
	}
	
def get_torrents():
	"""
	Returns a list of all torrent objects currently stored in the database.
	"""
	return [db.Torrent(key.lstrip('!')) for key in db.client.keys('!*')]
