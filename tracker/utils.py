import struct
import socket
import binascii
from bzrlib import bencode
from werkzeug import Response
import db
from rtracker.common.utils import mc

INTERVAL = 1000

def compact(ip, port, ascii=False):
	"""
	Compact IP address and port.

	>>> compact('127.0.0.1', 6667, ascii=True)
	'7f0000011a0b'
	>>> compact('127.0.0.1', 6667) == '7f0000011a0b'.decode('hex')
	True
	"""
	compacted = struct.pack('!4sH', socket.inet_aton(ip), port)
	return binascii.hexlify(compacted) if ascii else compacted
	
def expand(compacted):
	"""
	Expand compacted IP address and port.
	
	>>> expand('7f0000011a0b'.decode('hex'))
	('127.0.0.1', 6667)
	>>> expand('7f0000011a0b')
	('127.0.0.1', 6667)
	"""
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
	key = 'scrapedict_%s' % torrent
	scrape = mc.get(key)
	if scrape is None:
		scrape = {
			torrent.binary_hash(): {
				'complete': len(torrent.find_peers(status='seed')),
				'downloaded': torrent.completed(),
				'incomplete': len(torrent.find_peers(status='leech')),
			},
		}
		mc.set(key, scrape, INTERVAL)
	return scrape
	
def get_torrents():
	"""
	Returns a list of all torrent objects currently stored in the database.
	"""
	key = 'get_torrents'
	torrents = mc.get(key)
	if torrents is None:
		torrents = [db.Torrent(key.lstrip('!')) for key in db.client.keys('!*')]
		mc.set(key, torrents, INTERVAL)
	return torrents
