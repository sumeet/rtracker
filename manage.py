#!/usr/bin/env python

from werkzeug import script
from werkzeug.contrib import profiler
import tracker.main
import tracker.tests
import sys

def make_app():
	return tracker.main.application

action_runserver = script.make_runserver(make_app, use_reloader=True)
action_shell = script.make_shell(use_ipython=True)
action_profile = profiler.make_action(make_app)

def action_syncviews():
	"""
	Synchronize views to CouchDB.
	"""
	from webui import couchdb_views
	from couchdb.design import ViewDefinition
	import webui.db
	try:
		ViewDefinition.sync_many(webui.db.database, couchdb_views.view_definitions)
	except AttributeError:
		print 'Error: CouchDB must not be running'
		sys.exit(1)

if __name__ == '__main__':
	script.run()
