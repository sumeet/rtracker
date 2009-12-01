import hunnyb
import simplejson
import binascii
from hashlib import sha1

class TorrentFile:
	def __init__(self, data):
		if isinstance(data, str):
			self.__dict__ = self._torrent_to_dict(data)
			self.torrent_file = data
		elif isinstance(data, dict):
			self.__dict__ = data
			self.torrent_file = self._dict_to_torrent(data)

		if 'info_hash' not in self.__dict__.keys():
			self.info_hash = self._info_hash()
			
		self.dictionary = self._torrent_dict(self.__dict__)

	def __getattr__(self, key):
		return spaceless_dict(self.__dict__)[key]
		
	def __repr__(self):
		return '<TorrentFile %s: %s>' % (repr(self.info.get('name')), repr(self.info_hash))
		
	def _info_hash(self):
		return sha1(hunnyb.encode(hunnyb.decode(self.torrent_file).get('info'))).hexdigest()
		
	@staticmethod
	def _torrent_to_dict(data):
		dictionary = hunnyb.decode(data)
		dictionary['info']['pieces'] = binascii.hexlify(dictionary['info']['pieces'])
		return unicode_dict(dictionary)
		
	@staticmethod
	def _torrent_dict(data):
		return dict(
			[(key, value) for key,value in data.iteritems() if 
				(key in ['announce', 'created by', 'creation date', 'encoding', 'info'])
				and
				(value is not None)
			]
		)
		
	def _dict_to_torrent(self, data):
		dictionary = utf8_dict(self._torrent_dict(data))
		dictionary['info']['pieces'] = binascii.unhexlify(dictionary['info']['pieces'])
		return hunnyb.encode(dictionary)
		
# inspired by http://mail.python.org/pipermail/python-list/2009-June/183752.html
def utf8_dict(d):
	"""Change Unicode objects to UTF-8 encoded strings because hunnyb likes them"""
	if isinstance(d, dict):
		return dict([(utf8_dict(k), utf8_dict(v)) for k,v in d.iteritems()])
	elif isinstance(d, list):
		return [utf8_dict(x) for x in d]
	elif isinstance(d, unicode):
		return d.encode('utf-8')
	else:
		return d

def unicode_dict(d):
	"""Change strings to Unicode objects because python-couchdb likes them"""
	if isinstance(d, dict):
		return dict([(unicode_dict(k), unicode_dict(v)) for k,v in d.iteritems()])
	elif isinstance(d, list):
		return [unicode_dict(x) for x in d]
	elif isinstance(d, str):
		try:
			return d.decode('utf-8')
		except UnicodeDecodeError:
			return d.decode('iso-8859-1').encode('utf-8').decode('utf-8')
	else:
		return d

def spaceless_dict(d):
	"""Change spaces in dictionary keys to underscores because Python likes them"""
	if isinstance(d, dict):
		return dict([(k.replace(' ', '_'), spaceless_dict(v)) for k,v in d.iteritems()])
	elif isinstance(d, list):
		return [spaceless_dict(x) for x in d]
	else:
		return d
