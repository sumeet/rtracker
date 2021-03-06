from base64 import binascii

import cluster
from rtracker.common.utils import mc
from rtracker import settings
import utils

KEEP_KEYS = 10 * 60 # expire peers after not hearing from them
INTERVAL = 180

if len(settings.redis_servers) > 1:
	client = cluster.RedisCluster(settings.redis_servers)
else:
	client = settings.redis_servers[0]

class TorrentAlreadyExists(Exception):
	def __init__(self, info_hash):
		self.info_hash = info_hash
	def __str__(self):
		return repr(self.info_hash)

class TorrentUnregistered(Exception):
	def __init__(self, info_hash):
		self.info_hash = info_hash
	def __str__(self):
		return repr(self.info_hash)

class Torrent:
	def __init__(self, info_hash, create=False):
		"""
		Loads a torrent object (use argument create=True for a new torrent).

		Try loading a bad torrent:
		>>> torrent = Torrent('bad_hash')
		Traceback (most recent call last):
			...
		TorrentUnregistered: 'bad_hash'
		"""
		if len(info_hash) == 40:
			self.info_hash = info_hash
		elif len(info_hash) == 20:
			self.info_hash = binascii.hexlify(info_hash)
		else:
			raise TorrentUnregistered(info_hash)

		if create:
			self._create()
			return

		if not self._exists():
			raise TorrentUnregistered(self.info_hash)

	def find_peers(self, ip=None, port=None, status=None):
		return client.keys('%d:%s:%s' % (
			hash(self.info_hash),
			'*' if status is None
				else 's' if status.startswith('s')
				else 'l' if status.startswith('l')
				else '*',
			'*' if (ip is None or port is None)
				else utils.compact(ip, port, ascii=True)
		))

	def delete_peer(self, ip, port):
		client.delete(
			'%d:s:%s' % ( # If the peer is a seed
				hash(self.info_hash), utils.compact(ip, port, ascii=True)
			),
			'%d:l:%s' % ( # If the peer is a leecher
				hash(self.info_hash), utils.compact(ip, port, ascii=True)
			)
		)

	def register_peer(self, ip, port, uploaded, downloaded, left):
		key = '%d:%s:%s' % (
			hash(self.info_hash),
			's' if left == 0 else 'l',
			utils.compact(ip, port, ascii=True)
		)
		self.delete_peer(ip, port)
		client.set(key, 1)
		client.expire(key, KEEP_KEYS)

	def get_peerlist(self):
		key = 'get_peerlist_%s' % self.info_hash
		peerlist = mc.get(key)
		if peerlist is None:
			peerlist = ''.join(
				[binascii.unhexlify(peer.split(':')[2])
					for peer in self.find_peers()]
			)
			mc.set(key, peerlist, INTERVAL)
		return peerlist

	def register_completed(self):
		return client.incr(self._key())

	def completed(self):
		return int(client.get(self._key()))

	def binary_hash(self):
		return binascii.unhexlify(self.info_hash)

	def delete(self):
		for peer in self.find_peers():
			client.delete(peer)
		result = client.delete(self._key())
		client.save()
		return result

	def _key(self):
		return '!%s' % self.info_hash

	def _exists(self):
		return client.exists(self._key())

	def _create(self):
		result = client.setnx(self._key(), 0)
		if not result:
			raise TorrentAlreadyExists(self.info_hash)
		client.save()
		return result
