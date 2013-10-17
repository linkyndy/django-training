from itertools import chain, combinations

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

	def score_by_answers(answers):
		"""Returns the summed up score of given answers"""

		return sum([answer.score for answer in answers])

	def result_by_score(score):
		"""Returns test result based on given score"""

		try:
			return Result.objects.filter(test__pk=test_id, \
										 limit__lte=score) \
				  				 .order_by('-limit')[0]
		except IndexError:
			return None

	def similar_results(answers):
		"""
		Attempts to find better/worse result on test, by finding the 
		least amount of unchecked answers that will change the overall result.
		"""

		# Get unchecked answers
		unchecked = Answer.objects.filter(question__page__test__pk=test_id) \
								  .exclude(pk__in=[a.pk for a in answers]) \
								  .order_by('question')

		# Generate all combinations of unchecked answers, starting with fewer
		# elements/combination (in order to find the least amount of answers)
		combs = chain.from_iterable(combinations(unchecked, r) for r in range(len(unchecked)+1))

		for comb in combs:
			# Get result with unchecked answers from combination added
			similar_result = result_by_score(score_by_answers(comb) + score)

			# If result changes, return the new result
			if similar_result != None and \
			   similar_result.limit > result.limit:
				return {
					'result': similar_result,
					'answers': comb,
				}

		return None

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

	# Checked answers list
	checked = []

	# For each test question, get the answer ids from the session,
	# fetch the Answer objects, and store them in a list
	for question in questions:
		answer_ids = request.session['answers'].pop('question_{id}'.format(id=question.pk))

		for answer_id in answer_ids:
			checked.append(Answer.objects.get(pk=answer_id))

	# Compute test score and result text
	score = score_by_answers(checked)
	result = result_by_score(score)

	context = {
		'score': score,
		'result': result,
		'similar_results': similar_results(checked),
	}

	return render(request, 'tests/result.html', context)