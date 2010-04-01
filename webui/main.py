from werkzeug.routing import Map, Rule
from werkzeug import Request, Response, responder
import views

url_map = Map([
	Rule('/', endpoint='webui'),
	Rule('/download', endpoint='download'),
	Rule('/login', endpoint='login'),
	Rule('/upload', endpoint='upload'),
	Rule('/torrent_info', endpoint='torrent_info'),
	Rule('/delete', endpoint='delete'),
])
	
views = {
	'webui': views.torrents,
	'download': views.torrent_file,
	'login': views.login,
	'upload': views.upload,
	'torrent_info': views.torrent_info,
	'delete': views.delete,
}

class LargeFileRequest(Request):
	max_content_length = 20 * 1024 * 1024

@responder
def application(environ, start_response):
	request = LargeFileRequest(environ)
	urls = url_map.bind_to_environ(environ)
	return urls.dispatch(lambda e, v: views[e](request, **v), catch_http_exceptions=True)
