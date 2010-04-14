import db
import utils
import urlparse

# Backwards compatibility for Python 2.5
if not hasattr(urlparse, 'parse_qs'):
	import cgi as urlparse

import urllib

# implementing the BitTorrent Tracker Protocol from http://wiki.theory.org/BitTorrent_Tracker_Protocol

FAILURE_CODES = {
	100: 'Invalid request type: client request was not a HTTP GET',
	101: 'Missing info_hash',
	102: 'Missing peer_id',
	103: 'Missing port',
	150: 'Invalid infohash: infohash is not 20 bytes long',
	151: 'Invalid peerid: peerid is not 20 bytes long',
	152: 'Invalid numwant. Client requested more peers than allowed by tracker',
	200: 'info_hash not found in the database',
	500: 'Client sent an eventless request before the specified time',
	900: 'Generic error',
}

INTERVAL = 180 # seconds

def failure(code=900):
	if code not in FAILURE_CODES:
		code = 900
			
	data = {
		'failure reason': FAILURE_CODES.get(code),
		'failure code': code,
	}
	
	return utils.bResponse(data)

def announce(request):
	if request.method != 'GET':
		return failure(100)
	if 'info_hash' not in request.args:
		return failure(101)
	if 'port' not in request.args:
		return failure(103)

	info_hash = urlparse.parse_qs(request.query_string)['info_hash'][0]
	
	if len(info_hash) != 20:
		info_hash = urllib.unquote(info_hash)

	port = request.args.get('port', type=int)
	ip = request.args.get('ip', request.remote_addr)
	uploaded = request.args.get('uploaded', type=int)
	downloaded = request.args.get('downloaded', type=int)
	left = request.args.get('left', type=int)
	event = request.args.get('event')
	
	try:
		torrent = db.Torrent(info_hash)
	except db.TorrentUnregistered:
		return failure(200)

	if event == 'stopped':
		torrent.delete_peer(ip, port)
		return utils.bResponse('OK')
		
	if event == 'completed':
		torrent.register_completed()
		
	torrent.register_peer(ip, port, uploaded, downloaded, left)

	data = {
		'interval': INTERVAL,
		'peers': torrent.get_peerlist(),
	}

	return utils.bResponse(data)
	
def scrape(request):
	if request.method != 'GET':
		return failure(100)
		
	if 'info_hash' in request.args:
		info_hashes = urlparse.parse_qs(request.query_string)['info_hash']
	
		for (i, info_hash) in enumerate(info_hashes):
			if len(info_hash) != 20:
				info_hashes[i] = urllib.unquote(info_hash)
		
		try:
			torrents = [db.Torrent(info_hash) for info_hash in info_hashes]
		except db.TorrentUnregistered:
			return failure(200)
		
	else:
		torrents = utils.get_torrents()
		
	files = {}
	
	for torrent in torrents:
		files.update(utils.scrapedict(torrent))
		
	data = {'files': files ,}
	
	return utils.bResponse(data)
