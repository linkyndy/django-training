from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from models import Test, Question, Answer, Result
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
		request.session['answers'] = {}

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
			# Save answers in session
			request.session['answers'].update(form.cleaned_data)

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

	request.session.pop('test_status', None)
	request.session.pop('test_id', None)
	request.session.pop('page_number', None)
	request.session.pop('page_count', None)

	return redirect('tests:index')


def result(request, test_id):
	"""Displays the result of a test"""

	# If a test is not finished, go to that test
	if 'test_status' in request.session and \
	   request.session['test_status'] != 'finished':
		return redirect('tests:view', test_id)

	# If test is finished, but given test_id doesn't match
	# the current test, redirect to that test's result
	if request.session['test_id'] != test_id:
		return redirect('tests:result', request.session['test_id'])

	# Fetch test questions
	questions = Question.objects.filter(page__test__pk=test_id)

	answers = []

	# For each test question, get the answer id from the session,
	# fetch the Answer object, and store it in a list
	for question in questions:
		answer_id = request.session['answers'].pop('question_{id}'.format(id=question.pk))
		answers.append(Answer.objects.get(pk=answer_id))
	
	# Compute test score and result text
	score = sum([answer.score for answer in answers])
	text = Result.objects.filter(test__pk=test_id, limit__lte=score).order_by('-limit')[0]

	context = {
		'score': score,
		'text': text,
	}

	return render(request, 'tests/result.html', context)