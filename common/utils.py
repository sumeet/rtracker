from werkzeug import Response
import simplejson
import memcache

mc = memcache.Client(['127.0.0.1:11211'])

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