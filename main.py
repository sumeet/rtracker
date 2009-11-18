#!/usr/bin/env python
import os
from werkzeug.routing import Map, Rule, Submount
from werkzeug import Request, Response, responder
import tracker.views
import webui.views

root_path = os.path.abspath(os.path.dirname(__file__))

url_map = Map([
	Rule('/announce', endpoint='announce'),
	Rule('/scrape', endpoint='scrape'),
	Submount('/webui', [
		Rule('/', endpoint='webui'),
		Rule('/download', endpoint='download'),
		Rule('/login', endpoint='login'),
		Rule('/upload', endpoint='upload'),
	]),
])
	
views = {
	'announce': tracker.views.announce,
	'scrape': tracker.views.scrape,
	'webui': webui.views.torrents,
	'download': webui.views.torrent_file,
	'login': webui.views.login,
	'upload': webui.views.upload
}

@responder
def application(environ, start_response):
	request = Request(environ)
	urls = url_map.bind_to_environ(environ)
	return urls.dispatch(lambda e, v: views[e](request, **v), catch_http_exceptions=True)
	
if __name__ == '__main__':
	from werkzeug import run_simple
	run_simple('0.0.0.0', 4000, application)
