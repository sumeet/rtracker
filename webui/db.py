from couchdb import schema
import couchdb.client
import utils
import tracker.db
import datetime

database = couchdb.client.Database('http://localhost:5984/rtracker')

class Torrent(couchdb.schema.Document):
	def __init__(self, data=None, **kwargs):
		if data:
			if isinstance(data, dict):
				torrent_file = utils.TorrentFile(data)
			elif isinstance(data, utils.TorrentFile):
				torrent_file = data
			elif hasattr(data, 'read'):
				torrent_file = utils.TorrentFile(data.read(2 * 1024 * 1024))
			kwargs.update(dict([(str(key),val) for key,val in utils.spaceless_dict(torrent_file.dictionary).iteritems()]))
			return super(Torrent, self).__init__(id=torrent_file.info_hash, **kwargs)
		else:
			return super(Torrent, self).__init__(**kwargs)
	
	announce = schema.TextField()
	created_by = schema.TextField(name='created by')
	creation_date = schema.IntegerField(name='creation date')
	encoding = schema.TextField()
	info = schema.DictField()
	
	pub_date = schema.DateTimeField(default=datetime.datetime.now())
	uploaded_by = schema.TextField()
		
	type = schema.TextField(default='torrent')
	
	def tracker(self, **kwargs):
		return tracker.db.Torrent(self.id, **kwargs)
		
	def store(self, db=database):
		self.tracker(create=True)
		super(Torrent, self).store(db)
		
	def delete(self, db=database):
		self.tracker().delete()
		return db.delete(self.id)
		
	@classmethod
	def by_pub_date(cls, db=database, descending=True):
		return list(cls.view(db, 'torrents/by_pub_date', descending=descending, include_docs=True))
		
	@classmethod
	def get(cls, db=database, info_hash=None, name=None):
		if info_hash:
			return cls.load(db, info_hash)
		elif name:
			return list(cls.view(db, 'torrents/by_name', include_docs=True)[name])[0]
		