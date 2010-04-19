import unittest
import utils
from werkzeug import Response, Request, EnvironBuilder

class TestJSONResponse(unittest.TestCase):
	"""
	Tests for the JSONResponse decorator.
	"""
	
	def test_json_view_function_without_callback(self):
		@utils.JSONResponse
		def view_func(request):
			return 'a string'
		request = Request(EnvironBuilder(method='GET').get_environ())
		response = view_func(request)
		self.assertEqual(response.data, '"a string"')
		self.assertEqual(response.content_type,
			'application/javascript; charset=utf-8')
			
	def test_json_view_function_with_callback(self):
		@utils.JSONResponse
		def view_func(request):
			return 'a string'
		request = Request(
			EnvironBuilder(
				method='GET',
				query_string={'callback': 'callback'}
			).get_environ()
		)
		response = view_func(request)
		self.assertEqual(response.data, 'callback("a string");')
		self.assertEqual(response.content_type,
			'application/javascript; charset=utf-8')