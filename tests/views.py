from django.http import HttpResponse
from django.shortcuts import render, redirect

from models import Test


def index(request):
	"""Base view, showing all tests"""

	context = {
		'tests': Test.objects.all(),
		'active_test': request.session.get('test_id', None)
	}

	return render(request, 'tests/index.html', context)


def view(request, test_id):
	"""Test view, displays a test"""

	if 'test_id' in request.session and \
	   request.session['test_id'] != test_id:
		return redirect('tests:view', test_id=request.session['test_id'])

	if 'test_id' not in request.session:
		request.session['test_id'] = test_id

	page_number = request.session.get('page_number', 0)
	page = Test.objects.get(pk=test_id).pages.all()[page_number]

	return HttpResponse('View test #%s, page #%s' % (test_id, page.id))


def give_up(request):
	"""Give up current test, stored in the session"""

	request.session.pop('test_id', None)
	request.session.pop('page_number', None)
	return redirect('tests:index')


def result(request, test_id):
	"""Displays the result of a test"""

	return HttpResponse('Result for test #%s' % test_id)