#!/usr/bin/env python
import os
from werkzeug.routing import Map, Rule
from werkzeug import Request, Response, responder
import announce.views

root_path = os.path.abspath(os.path.dirname(__file__))

url_map = Map([
	Rule('/announce', endpoint='announce'),
	])
	
views = {'announce': announce.views.announce }

@responder
def application(environ, start_response):
	request = Request(environ)
	urls = url_map.bind_to_environ(environ)
	return urls.dispatch(lambda e, v: views[e](request, **v), catch_http_exceptions=True)
	
if __name__ == '__main__':
	from werkzeug import run_simple
	run_simple('localhost', 4000, application)