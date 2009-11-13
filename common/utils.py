from werkzeug import Response
import simplejson
from werkzeug.contrib.cache import MemcachedCache

mc = MemcachedCache(['127.0.0.1:11211'])

class JSONResponse:
	def __init__(self, func):
		self.func = func
		
	def __call__(self, request):
		json = simplejson.dumps(self.func(request))
		callback = request.args.get('callback')
		if callback:
			json = '%s(%s);' % (callback, json)
		return Response(json, mimetype='application/javascript')
		
class Memcache:
	def __init__(self, key, ttl=60*10, request_args=[]):
		self.key = key
		self.ttl = ttl
		self.request_args = request_args
		
	def __call__(self, func):
		def wrapped(*args, **kwargs):
			key = str(hash(self.key + ':'.join([args[0].args.get(request_arg, '') for request_arg in self.request_args])))
			data = mc.get(key)
			if data is None:
				data = func(*args, **kwargs)
				mc.set(key, data, self.ttl)
			return data
		return wrapped
