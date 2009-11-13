function(doc) {
  if (doc.type == "torrent") {
    if (doc.info.files) {
      var num_files = doc.info.files.length;
    } else {
      var num_files = 1;
    }
    var val = {
      "size": (doc.info.pieces.length / 40) * doc.info['piece length'],
      "name": doc.info.name,
      "num_files": num_files,
      "uploaded_by": doc.uploaded_by,
      "category": doc.category
    };
    emit(doc.pub_date, val);
  }
}