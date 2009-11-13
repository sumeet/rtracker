import db
from common.utils import JSONResponse, Memcache
import tracker.db
from werkzeug import Response

@JSONResponse
@Memcache('torrent_overview', ttl=60*10)
def torrents(request):
	torrent_list = []
	for torrent in db.database.view('torrent_info/by_pub_date', descending=True):
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
		headers=[('Content-Disposition', 'attachment; filename=%s.torrent' % torrent.info.get('name'))],
		mimetype='application/x-bittorrent')