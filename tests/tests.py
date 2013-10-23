from django.test import TestCase
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
		self.assertTemplateUsed(response, 'tests/index.html')


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