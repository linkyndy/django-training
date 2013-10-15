from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from models import Test
from forms import PageForm


def index(request):
	"""Base view, showing all tests"""

	context = {
		'tests': Test.objects.all(),
		'test_status': request.session.get('test_status', None),
		'active_test': request.session.get('test_id', None),
	}
	
	return render(request, 'tests/index.html', context)


def view(request, test_id):
	"""Test view, displays a test's pages"""

	# If another test is started, go to that test
	if 'test_id' in request.session and \
	   request.session['test_id'] != test_id:
		return redirect('tests:view', request.session['test_id'])

	# Attempt to load the test with test_id
	test = get_object_or_404(Test, pk=test_id)

	# If test_id is not started, start it
	if 'test_id' not in request.session:
		request.session['test_status'] = 'active'
		request.session['test_id'] = test_id
		request.session['page_number'] = 1
		request.session['page_count'] = test.pages.count()

	page_number = request.session['page_number']
	page_count = request.session['page_count']

	# This means that a test is finished, so proceed to the results
	if request.session['test_status'] == 'finished':
		return redirect('tests:result', test_id)

	page = test.pages.all()[page_number-1]

	# If page form has been submitted
	if request.method == 'POST':
		form = PageForm(request.POST, page=page)

		if form.is_valid():
			# Check if there is another page from the test; if not
			# proceed to the results
			if page_number < page_count:
				request.session['page_number'] += 1
				return redirect('tests:view', test_id)
			else:
				request.session['test_status'] = 'finished'
				return redirect('tests:result', test_id)
	else:
		form = PageForm(page=page)

	# Assign context variables
	context = {
		'test': test,
		'page_number': page_number,
		'page_count': page_count,
		'form': form,
	}
	
	return render(request, 'tests/view.html', context)


def give_up(request):
	"""Give up current test, stored in the session"""

	del request.session['test_status']
	del request.session['test_id']
	del request.session['page_number']
	del request.session['page_count']
	return redirect('tests:index')


def result(request, test_id):
	"""Displays the result of a test"""

	return HttpResponse('Result for test #%s' % test_id)