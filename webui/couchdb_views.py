from couchdb.design import ViewDefinition

"""
A list containing all of the views that we use for queries.
"""
view_definitions = [
	ViewDefinition(
		'categories',
		'names',
		'''
		function (doc) {
			if (doc.type == "torrent") {
				emit(doc.category, 1);
			}
		}
		''',
		'''
		function(key, values, rereduce) {
			return sum(values);
		}
		'''
	),
	ViewDefinition(
		'torrent_info',
		'by_pub_date',
		'''
		function(doc) {
			if (doc.type == "torrent") {
				if (doc.info.files) {
					var num_files = doc.info.files.length;
				} else {
					var num_files = 1;
				}
				var val = {
					"size": (doc.info.pieces.length / 40) *
						doc.info['piece length'],
					"name": doc.info.name,
					"num_files": num_files,
					"uploaded_by": doc.uploaded_by,
					"category": doc.category
				};
				emit(doc.pub_date, val);
			}
		}
		'''
	),
	ViewDefinition(
		'torrent_info_detailed',
		'by_info_hash',
		'''
		function(doc) {
			if (doc.type == "torrent") {
				if (doc.info.files) {
					var num_files = doc.info.files.length;
					var files = [];
					for (var i = 0; i < doc.info.files.length; i++) {
						files.push(doc.info.files[i].path.join("/"));
					}
					files.sort();
				} else {
					var num_files = 1;
					var files = [doc.info.name];
				}
				var val = {
					"size": (doc.info.pieces.length / 40) *
						doc.info['piece length'],
					"name": doc.info.name,
					"files": files,
					"num_files": num_files,
					"uploaded_by": doc.uploaded_by,
					"category": doc.category
				};
				emit(doc._id, val);
			}
		}
		'''
	),
	ViewDefinition(
		'torrent_name',
		'by_info_hash',
		'''
		function(doc) {
			if (doc.type == "torrent") {
				emit(doc._id, doc.info.name);
			}
		}
		'''
	),
	ViewDefinition(
		'torrents',
		'by_name',
		'''
		function(doc) {
			if (doc.type == "torrent") {
				doc.info_hash = doc._id;
				doc.size = (doc.info.pieces.length / 40) *
					doc.info['piece length'];
				emit(doc.info.name, doc);
			}
		}
		'''
	),
	ViewDefinition(
		'users',
		'by_username,password',
		'''
		function(doc) {
			if (doc.type == "user") {
				if (doc.admin) {
					var admin = true;
				} else {
				var admin = false;
				}
				emit([doc._id, doc.password], { "admin": admin });
			}
		}
		'''
	)
]