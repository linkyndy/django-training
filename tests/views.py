from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from models import Test


def index(request):
	"""Base view, showing all tests"""

	context = {
		'tests': Test.objects.all(),
		'active_test': request.session.get('test_id', None),
	}

	return render(request, 'tests/index.html', context)


def view(request, test_id):
	"""Test view, displays a test's pages"""

	# Attempt to load the test with test_id
	test = get_object_or_404(Test, pk=test_id)

	# If another test is started, go to that test
	if 'test_id' in request.session and \
	   request.session['test_id'] != test_id:
		return redirect('tests:view', test_id=request.session['test_id'])

	# If test_id is not started, start it
	if 'test_id' not in request.session:
		request.session['test_id'] = test_id

	# Get active test's current page number; if test
	# has been activated now, get default page number
	page_number = request.session.get('page_number', 0)

	page = test.pages.all()[page_number]
	page_count = test.pages.count()

	# Assign context variables
	context = {
		'test': test,
		'questions': page.questions.all(),
		'page_number': page_number,
		'page_count': page_count
	}

	return render(request, 'tests/view.html', context)


def give_up(request):
	"""Give up current test, stored in the session"""

	request.session.pop('test_id', None)
	request.session.pop('page_number', None)
	return redirect('tests:index')


def result(request, test_id):
	"""Displays the result of a test"""

	return HttpResponse('Result for test #%s' % test_id)