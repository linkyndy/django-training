from django.http import HttpResponse
from django.shortcuts import render

from models import Test


def index(request):
	"""Base view, showing all tests"""

	context = {'tests': Test.objects.all()}

	return render(request, 'tests/index.html', context)


def view(request, test_id):
	"""Test view, displays a test"""

	return HttpResponse('View test #%s' % test_id)


def result(request, test_id):
	"""Displays the result of a test"""

	return HttpResponse('Result for test #%s' % test_id)