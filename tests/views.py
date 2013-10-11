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
		request.session['page_number'] = 0
		request.session['score'] = 0

	page_count = test.pages.count()
	page_number = request.session['page_number']
	page = test.pages.all()[page_number]

	question_count = page.questions.count()

	errors = None

	# If page form has been submitted
	if request.method == 'POST':
		# Check whether data is valid
		for i in range(0, question_count):
			if 'q'+str(i) not in request.POST:
				errors = 'No answer'

		if errors is None:
			# Check if there is another page
			if page_number+1 < page_count:
				page_number += 1
				request.session['page_number'] += 1
			else:
				request.session.pop('test_id', None)
				request.session.pop('page_number', None)
				return redirect('tests:result')
	else:
		pass

	page = test.pages.all()[page_number]
	questions = page.questions.all()

	# Assign context variables
	context = {
		'test': test,
		'questions': questions,
		'page_number': page_number,
		'page_count': page_count,
		'errors': errors
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