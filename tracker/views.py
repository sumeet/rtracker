import db
import utils

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

INTERVAL = 15 # seconds

def failure(code=900):
	if code not in FAILURE_CODES:
		code = 900
			
	data = {
		'failure reason': FAILURE_CODES.get(code),
		'failure code': code,
	}
	
	return utils.bResponse(data)

def announce(request):
	request.charset = 'latin-1'
	
	if request.method != 'GET':
		return failure(100)
	if 'info_hash' not in request.args:
		return failure(101)
	if 'peer_id' not in request.args:
		return failure(102)
	if 'port' not in request.args:
		return failure(103)
	#if len(request.args.get('info_hash')) != 20:
	#	return failure(150)
	#if len(request.args.get('peer_id')) != 20:
	#	return failure(151)
		
	info_hash = request.args.get('info_hash').encode('iso-8859-1')
	peer_id = request.args.get('peer_id').encode('iso-8859-1')
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
		torrent.close()
		return utils.bResponse('OK')
		
	if event == 'completed':
		torrent.register_completed()
		
	torrent.register_peer(peer_id, ip, port, uploaded, downloaded, left)

	data = {
		'interval': INTERVAL,
		'peers': torrent.get_peerlist(info_hash),
	}
	
	torrent.close()
	
	return utils.bResponse(data)