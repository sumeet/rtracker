import unittest
import db
import views
import utils
from werkzeug import EnvironBuilder, Request, BaseResponse
import hunnyb

SAMPLE_HASH = '\x98H\x16\xfd2\x96"\x87n\x14\x90v4&No3.\x9f\xb3'
SAMPLE_HASH_HEX = '984816fd329622876e14907634264e6f332e9fb3'

# Test basic functionality. Add a torrent by info_hash, get announce and scrape, then delete the torrent
class TestTorrentDB(unittest.TestCase):
	def setUp(self):
		self.torrent = db.Torrent(SAMPLE_HASH, create=True)
	
	def tearDown(self):
		self.torrent.delete()
	
	def test_add_torrent_by_hex_encoded_hash(self):
		self.assertRaises(db.TorrentAlreadyExists, db.Torrent, SAMPLE_HASH_HEX, create=True)
		
	def test_delete_torrent(self):
		self.assert_(self.torrent.delete())
		

class TestViews(unittest.TestCase):
	def _build_announce_request_object(self, ip='1.1.1.1', port='1234', uploaded='0', downloaded='0', left='234', info_hash=SAMPLE_HASH, event=''):
		query_string = {
			'info_hash': info_hash,
			'ip': ip,
			'port': port,
			'uploaded': uploaded,
			'downloaded': downloaded,
			'left': left,
			'event': event,
		}
		
		return Request(EnvironBuilder(method='GET', query_string=query_string).get_environ())

	def setUp(self):
		self.torrent = db.Torrent(SAMPLE_HASH, create=True)
	
	def tearDown(self):
		self.torrent.delete()
		
	def test_announce(self):
		response_data = hunnyb.decode(views.announce(self._build_announce_request_object(ip='1.1.1.1', port='1234')).data)
		self.assert_(utils.compact('1.1.1.1', 1234) in response_data.get('peers'))
		
	def test_scrape(self):
		views.announce(self._build_announce_request_object(ip='1.1.1.1', port='1234', left='0', event='completed'))
		views.announce(self._build_announce_request_object(ip='2.2.2.2', port='1234', left='200'))
		
		# Scrape with info_hash specified
		query_string = { 'info_hash': SAMPLE_HASH }
		request = Request(EnvironBuilder(method='GET', query_string=query_string).get_environ())
		response_data = hunnyb.decode(views.scrape(request).data)
		self.assertEqual(response_data, {
			'files': {
				SAMPLE_HASH: {
					'complete': 1,
					'downloaded': 1,
					'incomplete': 1,
				}
			},
		})
		
		# Scrape with no info_hash specified
		request = Request(EnvironBuilder(method='GET', query_string=None).get_environ())
		response_data = hunnyb.decode(views.scrape(request).data)
		self.assertEqual(response_data.get('files').get(SAMPLE_HASH), {
				'complete': 1,
				'downloaded': 1,
				'incomplete': 1,
		})
		
def run_tests():
	for case in [TestTorrentDB, TestViews]:
		suite = unittest.TestLoader().loadTestsFromTestCase(case)
		unittest.TextTestRunner(verbosity=2).run(suite)