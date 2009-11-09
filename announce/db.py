import redis
import utils
from base64 import binascii

KEEP_KEYS = 10 * 60 # seconds to keep clients in the database

client = redis.Redis()

def find_peers(info_hash=None, ip=None, port=None, left=None):
	return client.keys('%s:%s:%s' % (
		'*' if info_hash is None else hash(info_hash),
		'*' if left is None else str(left),
		'*' if (ip is None or port is None) else utils.compact(ip, port, ascii=True)
	))

def delete_peer(info_hash, ip, port):
	for key in find_peers(info_hash=info_hash, ip=ip, port=port):
		client.delete(key)

def register_peer(info_hash, peer_id, ip, port, uploaded, downloaded, left):
	key = '%s:%d:%s' % (hash(info_hash), left, utils.compact(ip, port, ascii=True))
	delete_peer(info_hash, ip, port)
	client.set(key, 1)
	client.expire(key, KEEP_KEYS)
	
def get_peerlist(info_hash, numwant=50):
	return ''.join([binascii.unhexlify(peer.split(':')[2]) for peer in find_peers(info_hash=info_hash)])
	
def close():
	return client.disconnect()
	