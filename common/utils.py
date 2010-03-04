from werkzeug import Response
import simplejson
from werkzeug.contrib.cache import MemcachedCache

mc = MemcachedCache(['127.0.0.1:11211'], key_prefix='rtracker')

class JSONResponse:
	"""
	Decorator for view functions that transforms the return value into a JSON response.
	"""
	def __init__(self, func):
		self.func = func
		
	def __call__(self, request):
		json = simplejson.dumps(self.func(request), ensure_ascii=True)
		callback = request.args.get('callback')
		if callback:
			json = '%s(%s);' % (callback, json)
		return Response(json, content_type='application/javascript; charset=utf-8')


#class MemcacheResponse:
	"""
	Decorator for view functions that caches the return value, optionally based on request arguments.
	
	>>> class MockRequest(): pass
	... 
	>>> request1 = MockRequest()
	>>> setattr(request1, 'args', {'goob': 'town'})
	"""

class Memcache:
	"""
	Decorator to cache function output.
	
	>>> @Memcache('test', 1)
	... def test(n):
	... 	return(n + 1)
	... 
	>>> test(1)
	2
	>>> test(2)
	2
	"""
	def __init__(self, key, ttl=60*10):
		self.key = key
		self.ttl = ttl
		
	def __call__(self, func):
		def wrapped(*args, **kwargs):
			data = mc.get(self.key)
			if data is None:
				data = func(*args, **kwargs)
				mc.set(self.key, data, self.ttl)
			return data
		return wrapped
