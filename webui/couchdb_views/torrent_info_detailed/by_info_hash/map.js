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
      "size": (doc.info.pieces.length / 40) * doc.info['piece length'],
      "name": doc.info.name,
      "files": files,
      "num_files": num_files,
      "uploaded_by": doc.uploaded_by,
      "category": doc.category
    };
    emit(doc._id, val);
  }
}