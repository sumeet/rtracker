from werkzeug.routing import Map, Rule
from werkzeug import Request, Response, responder
import views

url_map = Map([
	Rule('/', endpoint='webui'),
	Rule('/download', endpoint='download'),
	Rule('/login', endpoint='login'),
	Rule('/upload', endpoint='upload'),
	Rule('/torrent_info', endpoint='torrent_info'),
])
	
views = {
	'webui': views.torrents,
	'download': views.torrent_file,
	'login': views.login,
	'upload': views.upload,
	'torrent_info': views.torrent_info,
}

@responder
def application(environ, start_response):
	request = Request(environ)
	urls = url_map.bind_to_environ(environ)
	return urls.dispatch(lambda e, v: views[e](request, **v), catch_http_exceptions=True)