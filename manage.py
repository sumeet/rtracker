#!/usr/bin/env python

from werkzeug import script
import main
import tracker.tests

action_runserver = script.make_runserver(main.application, use_reloader=True)
action_shell = script.make_shell(use_ipython=True)

def action_runtests():
	"""Run tests."""
	tracker.tests.run_tests()

if __name__ == '__main__':
	script.run()