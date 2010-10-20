import datetime
import threading

try:
	from couchdb import schema
	assert schema # For PyFlakes.
except ImportError:
	from couchdb import mapping as schema # For couchdb-python 0.7+
import couchdb.client

from rtracker.tracker import db as tracker_db
import utils

class Couch(threading.local):
	def __init__(self):
		threading.local.__init__(self)
		self.database = couchdb.client.Database(
			'http://localhost:5984/rtracker'
		)

database = Couch().database

class Torrent(schema.Document):
	def __init__(self, data=None, **kwargs):
		if data:
			if isinstance(data, dict):
				torrent_file = utils.TorrentFile(data)
			elif isinstance(data, utils.TorrentFile):
				torrent_file = data
			elif hasattr(data, 'read'):
				torrent_file = utils.TorrentFile(data.read())
			kwargs.update(dict([(str(key).replace(' ', '_'),val)
				for key,val in torrent_file.dictionary.iteritems()]))
			return super(Torrent, self).__init__(
				id=torrent_file.info_hash, **kwargs
			)
		else:
			return super(Torrent, self).__init__(**kwargs)

	announce = schema.TextField()
	created_by = schema.TextField(name='created by')
	creation_date = schema.IntegerField(name='creation date')
	encoding = schema.TextField()
	info = schema.DictField()

	pub_date = schema.DateTimeField()
	uploaded_by = schema.TextField()
	category = schema.TextField()

	type = schema.TextField(default='torrent')

	def tracker(self, **kwargs):
		return tracker_db.Torrent(self.id, **kwargs)

	def store(self, db=database):
		self.tracker(create=True)
		if not self.pub_date:
			self.pub_date = datetime.datetime.now()
		super(Torrent, self).store(db)
		db.put_attachment(
			db.get(self.id),
			self.get_file(),
			filename='torrent',
			content_type='application/x-bittorrent'
		)

	def delete(self, db=database):
		self.tracker().delete()
		return db.delete(db.get(self.id))

	def get_file(self):
		return utils.TorrentFile(dict(self.items())).torrent_file

	@classmethod
	def by_pub_date(cls, db=database, descending=True):
		return list(cls.view(
			db,
			'torrents/by_pub_date',
			descending=descending,
			include_docs=True)
		)

	@classmethod
	def get(cls, db=database, info_hash=None, name=None):
		if info_hash:
			return cls.load(db, info_hash)
		elif name:
			return list(cls.view(
				db,
				'torrents/by_name',
				include_docs=True
			)[name])[0]
