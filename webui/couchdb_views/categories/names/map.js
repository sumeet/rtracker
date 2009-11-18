function(doc) {
  if (doc.type == "torrent") {
    emit(doc.category, 1);
  }
}