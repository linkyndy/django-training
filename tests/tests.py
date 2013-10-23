from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from models import Test, Page, Question, Answer, Result


class NoTestsCreatedTests(TestCase):
	"""Tests for when no tests are created within the app"""

	def testIndex(self):
		response = self.client.get(reverse('tests:index'))

		self.assertEqual(response.status_code, 200)
		self.assertQuerysetEqual(response.context['tests'], [])
		self.assertEqual(response.context['test_status'], None)
		self.assertEqual(response.context['active_test'], None)


class SessionTests(TestCase):
	"""Session tests"""

	fixtures = ['sample_test.json']

	def setUp(self):
		self.client = Client()

	def testNoTestStarted(self):
		self.assertNotIn('test_status', self.client.session)
		self.assertNotIn('test_id', self.client.session)
		self.assertNotIn('page_number', self.client.session)
		self.assertNotIn('page_count', self.client.session)
		self.assertNotIn('answers', self.client.session)

	def testTestStarted(self):
		self.client.get(reverse('tests:view', args=(1,)))
		self.assertIn('test_status', self.client.session)
		self.assertEqual(self.client.session['test_status'], 'active')
		self.assertIn('test_id', self.client.session)
		self.assertEqual(self.client.session['test_id'], '1')
		self.assertIn('page_number', self.client.session)
		self.assertEqual(self.client.session['page_number'], 1)
		self.assertIn('page_count', self.client.session)
		self.assertEqual(self.client.session['page_count'], 3)
		self.assertIn('answers', self.client.session)
		self.assertEqual(self.client.session['answers'], {})

	def testTestStartedButGivenUp(self):
		self.client.get(reverse('tests:view', args=(1,)))
		self.client.get(reverse('tests:give_up'))
		self.assertNotIn('test_status', self.client.session)
		self.assertNotIn('test_id', self.client.session)
		self.assertNotIn('page_number', self.client.session)
		self.assertNotIn('page_count', self.client.session)
		self.assertNotIn('answers', self.client.session)

	def testOngoingAndFinishedTest(self):
		test = Test.objects.get(pk=1)
		pages = test.pages.all()

		self.client.get(reverse('tests:view', args=(1,)))
		data = {
			'question_1': ['4'],
			'question_2': ['5', '7'],
			'question_3': ['9', '10']
		}

		self.client.post(reverse('tests:view', args=(1,)), data)
		self.assertIn('test_status', self.client.session)
		self.assertEqual(self.client.session['test_status'], 'active')
		self.assertIn('test_id', self.client.session)
		self.assertEqual(self.client.session['test_id'], '1')
		self.assertIn('page_number', self.client.session)
		self.assertEqual(self.client.session['page_number'], 2)
		self.assertIn('page_count', self.client.session)
		self.assertEqual(self.client.session['page_count'], 3)
		self.assertIn('answers', self.client.session)
		self.assertNotEqual(self.client.session['answers'], {})
		data = {
			'question_4': ['11'],
			'question_5': ['13', '14'],
		}

		self.client.post(reverse('tests:view', args=(1,)), data)
		self.assertIn('test_status', self.client.session)
		self.assertEqual(self.client.session['test_status'], 'active')
		self.assertIn('test_id', self.client.session)
		self.assertEqual(self.client.session['test_id'], '1')
		self.assertIn('page_number', self.client.session)
		self.assertEqual(self.client.session['page_number'], 3)
		self.assertIn('page_count', self.client.session)
		self.assertEqual(self.client.session['page_count'], 3)
		self.assertIn('answers', self.client.session)
		self.assertNotEqual(self.client.session['answers'], {})
		data = {
			'question_6': ['15'],
			'question_7': ['22', '23'],
			'question_8': ['25'],
		}

		self.client.post(reverse('tests:view', args=(1,)), data)
		self.assertIn('test_status', self.client.session)
		self.assertEqual(self.client.session['test_status'], 'finished')
		self.assertIn('test_id', self.client.session)
		self.assertEqual(self.client.session['test_id'], '1')
		self.assertIn('page_number', self.client.session)
		self.assertEqual(self.client.session['page_number'], 3)
		self.assertIn('page_count', self.client.session)
		self.assertEqual(self.client.session['page_count'], 3)
		self.assertIn('answers', self.client.session)
		self.assertNotEqual(self.client.session['answers'], {})


class TemplateTests(TestCase):
	"""Template tests"""

	fixtures = ['sample_test.json']

	def setUp(self):
		self.client = Client()

	def testIndexTemplateUsed(self):
		response = self.client.get(reverse('tests:index'))
		self.assertTemplateUsed(response, 'tests/index.html')

	def testViewTemplateUsed(self):
		response = self.client.get(reverse('tests:view', args=(1,)))
		self.assertTemplateUsed(response, 'tests/view.html')

	def testResultTemplateUsed(self):
		self.client.get(reverse('tests:view', args=(1,)))
		self.client.post(reverse('tests:view', args=(1,)), {
			'question_1': ['4'],
			'question_2': ['5', '7'],
			'question_3': ['9', '10']
		})
		self.client.post(reverse('tests:view', args=(1,)), {
			'question_4': ['11'],
			'question_5': ['13', '14'],
		})
		self.client.post(reverse('tests:view', args=(1,)), {
			'question_6': ['15'],
			'question_7': ['22', '23'],
			'question_8': ['25'],
		})
		response = self.client.get(reverse('tests:result', args=(1,)))
		self.assertTemplateUsed(response, 'tests/result.html')


class IndexViewTests(TestCase):
	"""Tests involving the index view of the tests app"""

	fixtures = ['sample_test.json']

	def testContext(self):
		response = self.client.get(reverse('tests:index'))

		self.assertEqual(response.status_code, 200)
		self.assertQuerysetEqual(response.context['tests'], ['<Test: Basic test>'])
		self.assertEqual(response.context['test_status'], None)
		self.assertEqual(response.context['active_test'], None)
		self.assertTemplateUsed(response, 'tests/index.html')


class FlowTests(TestCase):
	"""Tests involving the app flow"""

	fixtures = ['sample_test.json']

	def testActiveTest(self):
		# Go to test page, e.g. start the test
		self.client.get(reverse('tests:view', args=(1,)))

		# Go back to index page and test context
		response = self.client.get(reverse('tests:index'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['test_status'], 'active')
		self.assertEqual(response.context['active_test'], '1')
		self.assertTemplateUsed(response, 'tests/index.html')