#!/usr/bin/env python

from werkzeug import script
from werkzeug.contrib import profiler
import tracker.main
import tracker.tests

def make_app():
	return tracker.main.application

action_runserver = script.make_runserver(make_app, use_reloader=True)
action_shell = script.make_shell(use_ipython=True)
action_profile = profiler.make_action(make_app)

def action_runtests():
	"""Run tests."""
	tracker.tests.run_tests()

if __name__ == '__main__':
	script.run()
