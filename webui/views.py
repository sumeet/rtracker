import db
from rtracker.common.utils import JSONResponse, Memcache, mc
from rtracker import tracker
from werkzeug import Response, redirect, Href
import hashlib

@JSONResponse
@Memcache('torrent_overview', ttl=60*3)
def torrents(request):
	torrent_list = []
	for torrent in db.database.view(
		'torrent_info/by_pub_date', descending=True
	):
		track = tracker.db.Torrent(torrent.id)
		torrent_list.append({
			'size': torrent.value.get('size'),
			'name': torrent.value.get('name'),
			'num_files': torrent.value.get('num_files'),
			'uploaded_by': torrent.value.get('uploaded_by'),
			'category': torrent.value.get('category'),
			'info_hash': torrent.id,
			'pub_date': torrent.key,
			'seeds': len(track.find_peers(status='seed')),
			'leechers': len(track.find_peers(status='leech')),
			'completed': track.completed(),
		})
	return torrent_list
	
def torrent_file(request):
	torrent = db.Torrent.get(info_hash=request.args.get('id'))
	return Response(torrent.get_file(),
		headers=[
			'Content-Disposition', 'attachment; filename="%s.torrent"' %
				torrent.info.get('name')
		],
		mimetype='application/x-bittorrent'
	)

@JSONResponse
def torrent_info(request):
	info_hash = request.args.get('id')
	key = 'torrent_info_%s' % info_hash
	interval = 2400
	information = mc.get(key)
	if information is None:
		information = list(db.database.view(
			'torrent_info_detailed/by_info_hash'
		)[info_hash])[0].value
		mc.set(key, information, interval)
	return information

class LoginRequired:
	def __init__(self, func):
		self.func = func
		
	def __call__(self, request):
		if request.method == 'POST':
			username = request.form.get('username')
			password = hashlib.md5(request.form.get('password')).hexdigest()
			if len(db.database.view(
				'users/by_username,password'
			)[username, password]) == 1:
				return self.func(request)
			else:
				return {'success': False}
		
		
@JSONResponse
@LoginRequired
def login(request):
	return {
		'success': True,
		'categories': [row.key
			for row in db.database.view('categories/names', group=True)]
	}
	
@JSONResponse
@LoginRequired
def upload(request):
	torrent = request.files.get('torrent')
	category = request.form.get('category')
	username = request.form.get('username')
	
	new_torrent = db.Torrent(torrent)
	new_torrent.category = category
	new_torrent.uploaded_by = username
	
	new_torrent.store()
	
	mc.delete('torrent_overview')
	
	return {
		'success': True
	}

@JSONResponse
@LoginRequired
def delete(request):
    torrent = request.form.get('torrent')
    db.Torrent.get(info_hash=torrent).delete()
    mc.delete('torrent_overview')
    return {
        'success': True
    }
