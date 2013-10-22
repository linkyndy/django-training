from django.test import TestCase
from django.core.urlresolvers import reverse

from models import Test, Page, Question, Answer, Result


class TestHelper(object):
	"""Helper class to leverage test creation in unittests"""

	def createOne(self):
		"""Create one test together with associated models"""

		# Create Test
		self.test = Test.objects.create(name='Name', description='Description')

		# Add associated data to Test
		page1 = Page.objects.create(name='Page1', test=self.test)
		page2 = Page.objects.create(name='Page2', test=self.test)

		question1 = Question.objects.create(name='Question1', page=page1)
		question2 = Question.objects.create(name='Question2', page=page1)
		question3 = Question.objects.create(name='Question3', page=page2)

		answer1 = Answer.objects.create(name='Answer1', score=1, question=question1)
		answer2 = Answer.objects.create(name='Answer2', score=2, question=question1)
		answer3 = Answer.objects.create(name='Answer3', score=3, question=question2)
		answer4 = Answer.objects.create(name='Answer4', score=4, question=question2)
		answer5 = Answer.objects.create(name='Answer5', score=5, question=question3)
		answer6 = Answer.objects.create(name='Answer6', score=6, question=question3)

		result1 = Result.objects.create(text='Result1', limit=1, test=self.test)
		result2 = Result.objects.create(text='Result2', limit=5, test=self.test)
		result3 = Result.objects.create(text='Result3', limit=10, test=self.test)

		self.repr = [repr(self.test)]
		return self.test

	def createN(self, n=2):
		self.tests = []
		self.repr = []

		for i in range(0, n):
			# Create Test
			test = Test.objects.create(name='Name{i}'.format(i=i), description='Description{i}'.format(i=i))
			
			# Add associated data to Test
			page1 = Page.objects.create(name='Page1', test=test)
			page2 = Page.objects.create(name='Page2', test=test)

			question1 = Question.objects.create(name='Question1', page=page1)
			question2 = Question.objects.create(name='Question2', page=page1)
			question3 = Question.objects.create(name='Question3', page=page2)

			answer1 = Answer.objects.create(name='Answer1', score=1, question=question1)
			answer2 = Answer.objects.create(name='Answer2', score=2, question=question1)
			answer3 = Answer.objects.create(name='Answer3', score=3, question=question2)
			answer4 = Answer.objects.create(name='Answer4', score=4, question=question2)
			answer5 = Answer.objects.create(name='Answer5', score=5, question=question3)
			answer6 = Answer.objects.create(name='Answer6', score=6, question=question3)

			result1 = Result.objects.create(text='Result1', limit=1, test=test)
			result2 = Result.objects.create(text='Result2', limit=5, test=test)
			result3 = Result.objects.create(text='Result3', limit=10, test=test)

			self.tests.append(test)
			self.repr.append(repr(test))

		return self.tests


class IndexViewTests(TestCase):
	"""Tests involving the index view of the tests app"""

	def testNoTestsCreated(self):
		response = self.client.get(reverse('tests:index'))

		self.assertEqual(response.status_code, 200)
		self.assertQuerysetEqual(response.context['tests'], [])
		self.assertEqual(response.context['test_status'], None)
		self.assertEqual(response.context['active_test'], None)
		self.assertTemplateUsed(response, 'tests/index.html')

	def testSomeTestsCreated(self):
		helper = TestHelper()
		helper.createN(2)

		response = self.client.get(reverse('tests:index'))

		self.assertEqual(response.status_code, 200)
		self.assertQuerysetEqual(response.context['tests'], helper.repr)
		self.assertEqual(response.context['test_status'], None)
		self.assertEqual(response.context['active_test'], None)
		self.assertTemplateUsed(response, 'tests/index.html')

	def testActiveTest(self):
		# Create stub test
		helper = TestHelper()
		helper.createOne()

		# Go to test page, e.g. start the test
		self.client.get(reverse('tests:view', args=(helper.test.pk,)))

		# Go back to index page and test context
		response = self.client.get(reverse('tests:index'))

		self.assertEqual(response.status_code, 200)
		self.assertQuerysetEqual(response.context['tests'], helper.repr)
		self.assertEqual(response.context['test_status'], 'active')
		self.assertEqual(response.context['active_test'], str(helper.test.pk))
		self.assertTemplateUsed(response, 'tests/index.html')