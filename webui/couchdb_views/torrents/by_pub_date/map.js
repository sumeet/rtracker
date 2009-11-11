function(doc) {
  if (doc.type == "torrent") {
    doc.info_hash = doc._id;
    doc.size = (doc.info.pieces.length / 40) * doc.info['piece length'];
    emit(doc.pub_date, doc);
  }
}