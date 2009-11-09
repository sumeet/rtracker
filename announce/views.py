from werkzeug import Response
import hunnyb
import db
import struct

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
			
	data = hunnyb.encode({
		'failure reason': FAILURE_CODES.get(code),
		'failure code': code,
	})
	
	return Response(data, mimetype='text/plain')

def announce(request):
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
		
	info_hash = request.args.get('info_hash')
	peer_id = request.args.get('peer_id')
	port = int(request.args.get('port'))
	ip = request.args.get('ip', request.remote_addr)
	uploaded = int(request.args.get('uploaded'))
	downloaded = int(request.args.get('downloaded'))
	left = int(request.args.get('left'))
	event = request.args.get('event')
	
	if event == 'stopped':
		db.delete_peer(info_hash, peer_id)
		return Response('OK', mimetype='text/plain')
		
	db.register_peer(info_hash, peer_id, ip, port, uploaded, downloaded, left)

	#peers = [{'id': peer.get('peer_id'), 'ip': peer.get('ip'), 'port': peer.get('port'),} for peer in db.get_peers(info_hash)]
	peers = []
	for peer in db.get_peers(info_hash):
		peers.append([hex(int(number)) for number in peer.get('ip').split('.')] + [hex(int(peer.get('port')))])
		
	print [hexed[0] + hexed[3] for hexed in peers]

	print peers
	interval = INTERVAL
	
	data = hunnyb.encode({
		'interval': interval,
		'peers': ''.join([hexed[0] + hexed[3] for hexed in peers]),
	})
	
	return Response(data, mimetype='text/plain')