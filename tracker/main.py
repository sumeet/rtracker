import os
from werkzeug.routing import Map, Rule
from werkzeug import Request, Response, responder
import views

root_path = os.path.abspath(os.path.dirname(__file__))

url_map = Map([
	Rule('/announce', endpoint='announce'),
	Rule('/scrape', endpoint='scrape'),
])
	
views = {
	'announce': views.announce,
	'scrape': views.scrape,
}

@responder
def application(environ, start_response):
	request = Request(environ)
	urls = url_map.bind_to_environ(environ)
	return urls.dispatch(lambda e, v: views[e](request, **v), catch_http_exceptions=True)
