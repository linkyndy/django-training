from django.http import HttpResponse


def index(request):
	"""Base view, showing all tests"""

	return HttpResponse('Tests index')


def view(request, test_id):
	"""Test view, displays a test"""

	return HttpResponse('View test #%s' % test_id)


def result(request, test_id):
	"""Displays the result of a test"""

	return HttpResponse('Result for test #%s' % test_id)