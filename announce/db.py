import redis
import random
import simplejson

KEEP_KEYS = 10 * 60 # seconds to keep clients in the database

client = redis.Redis()

def delete_peer(info_hash, peer_id):
	for key in client.keys('%s:*:%s' % (hash(info_hash), hash(peer_id))):
		client.delete(key)	

def register_peer(info_hash, peer_id, ip, port, uploaded, downloaded, left):
	peer = {
		'info_hash': info_hash,
		'peer_id': peer_id,
		'ip': ip,
		'port': port,
		'uploaded': uploaded,
		'downloaded': downloaded,
		'left': left,
	}
	
	key = '%s:%d:%s' % (hash(info_hash), left, hash(peer_id))
	
	delete_peer(info_hash, peer_id)
	
	client.set(key, simplejson.dumps(peer))
	client.expire(key, KEEP_KEYS)
	
def get_peers(info_hash, numwant=50, sorted=False, reverse=False):
	return [simplejson.loads(peer) for peer in client.mget(*client.keys('%s:*' % hash(info_hash)))]