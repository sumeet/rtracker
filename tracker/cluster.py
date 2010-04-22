from threading import Thread
from Queue import Queue

class RedisCluster(object):
	"""
	Basic Redis sharding.
	"""
	def __init__(self, redis_clients):
		"""
		`redis_clients` is a list of `redis.Redis` objects for separate redis
		instances.
		"""
		self.clients = redis_clients

	def keys(self, query='*'):
		queue = Queue()
		threads = []

		def _keys(_queue, _client, _query):
			_queue.put(_client.keys(_query))

		for client in self.clients:
			threads.append(Thread(
				target=_keys,
				args=[queue, client, query]
			))

		for thread in threads:
			thread.start()
			
		results = []
		for thread in threads:
			results.extend(queue.get())
		
		for thread in threads:
			thread.join()
			
		return results
	
	def delete(self, *keys):
		deleted_keys = 0
		for key in keys:
			deleted_keys += self.clients[self._hash(key)].delete(key)
		return deleted_keys

	def set(self, key, value, **kwargs):
		return self.clients[self._hash(key)].set(key, value, **kwargs)

	def expire(self, key, time):
		return self.clients[self._hash(key)].expire(key, time)

	def incr(self, key, amount=1):
		return self.clients[self._hash(key)].incr(key, amount)

	def get(self, key):
		return self.clients[self._hash(key)].get(key)

	def save(self):
		for client in self.clients:
			client.save()

	def exists(self, key):
		return self.clients[self._hash(key)].exists(key)

	def setnx(self, key, value):
		return self.clients[self._hash(key)].setnx(key, value)

	def _hash(self, key):
		return hash(key) % len(self.clients)
