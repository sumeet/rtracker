function(doc) {
  if (doc.type == "user") {
    if (doc.admin) {
      var admin = true;
    } else {
      var admin = false;
    }
    emit([doc._id, doc.password],
        { "admin": admin }
    );
  }
}