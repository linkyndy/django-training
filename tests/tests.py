from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from models import Test, Page, Question, Answer, Result
from forms import PageForm


class NoTestsCreatedTests(TestCase):
    """Tests for when no tests are created within the app"""

    def testIndexContext(self):
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
        session = self.client.session
        session['test_status'] = 'finished'
        session['answers'] = {
            'question_1': ['4'],
            'question_2': ['5', '7'],
            'question_3': ['9', '10'],
            'question_4': ['11'],
            'question_5': ['13', '14'],
            'question_6': ['15'],
            'question_7': ['22', '23'],
            'question_8': ['25'],
        }
        session.save()
        response = self.client.get(reverse('tests:result', args=(1,)))
        self.assertTemplateUsed(response, 'tests/result.html')


class IndexViewTests(TestCase):
    """Tests involving the index view of the tests app"""

    fixtures = ['sample_test.json']

    def testContext(self):
        response = self.client.get(reverse('tests:index'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('tests', response.context)
        self.assertQuerysetEqual(response.context['tests'],
                                 ['<Test: Basic test>'])
        self.assertIn('test_status', response.context)
        self.assertEqual(response.context['test_status'], None)
        self.assertIn('active_test', response.context)
        self.assertEqual(response.context['active_test'], None)


class ViewViewTests(TestCase):
    """Tests involving the view view of the tests app"""

    fixtures = ['sample_test.json']

    def testContext(self):
        response = self.client.get(reverse('tests:view', args=(1,)))

        self.assertEqual(response.status_code, 200)
        self.assertIn('test', response.context)
        self.assertEqual(response.context['test'], Test.objects.get(pk=1))
        self.assertIn('page_number', response.context)
        self.assertEqual(response.context['page_number'], 1)
        self.assertIn('page_count', response.context)
        self.assertEqual(response.context['page_count'], 3)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PageForm)


class ResultViewTests(TestCase):
    """Tests involving the result view of the tests app"""

    fixtures = ['sample_test.json']

    def testContext(self):
        self.client.get(reverse('tests:view', args=(1,)))
        session = self.client.session
        session['test_status'] = 'finished'
        session['answers'] = {
            'question_1': ['4'],
            'question_2': ['5', '7'],
            'question_3': ['9', '10'],
            'question_4': ['11'],
            'question_5': ['13', '14'],
            'question_6': ['15'],
            'question_7': ['22', '23'],
            'question_8': ['25'],
        }
        session.save()
        response = self.client.get(reverse('tests:result', args=(1,)))

        self.assertEqual(response.status_code, 200)
        self.assertIn('score', response.context)
        self.assertEqual(response.context['score'], 5)
        self.assertIn('result', response.context)
        self.assertEqual(response.context['result'],
                         Result(text='Your result is too low!',
                                limit=-999))
        self.assertIn('similar_results', response.context)
        self.assertEqual(response.context['similar_results'], {
            'better_result': {
                'result': Result.objects.get(limit=10),
                'answers': [Answer.objects.get(pk=20)]
            },
            'worse_result': None
        })


class FlowTests(TestCase):
    """Tests involving the app flow"""

    fixtures = ['sample_test.json']

    def setUp(self):
        self.client = Client()

    def testTestWithBothSimilarResults(self):
        self.client.get(reverse('tests:view', args=(1,)))

        session = self.client.session
        session['test_status'] = 'finished'
        session['answers'] = {
            'question_1': ['1', '4'],
            'question_2': ['5'],
            'question_3': ['9'],
            'question_4': ['12'],
            'question_5': ['13'],
            'question_6': ['15', '16'],
            'question_7': ['23'],
            'question_8': ['24'],
        }
        session.save()

        response = self.client.get(reverse('tests:result', args=(1,)))

        self.assertEqual(response.context['score'], 26)
        self.assertEqual(response.context['result'],
                         Result.objects.get(limit=20))
        self.assertEqual(response.context['similar_results'], {
            'better_result': {
                'result': Result.objects.get(limit=30),
                'answers': [Answer.objects.get(pk=14)]
            },
            'worse_result': {
                'result': Result(text='Your result is too low!',
                                 limit=-999),
                'answers': [Answer.objects.get(pk=17)]
            }
        })

    def testTestWithBetterSimilarResults(self):
        self.client.get(reverse('tests:view', args=(1,)))

        session = self.client.session
        session['test_status'] = 'finished'
        session['answers'] = {
            'question_1': ['2'],
            'question_2': ['7'],
            'question_3': ['8', '10'],
            'question_4': ['11'],
            'question_5': ['13'],
            'question_6': ['16'],
            'question_7': ['23'],
            'question_8': ['24'],
        }
        session.save()

        response = self.client.get(reverse('tests:result', args=(1,)))

        self.assertEqual(response.context['score'], 2)
        self.assertEqual(response.context['result'],
                         Result(text='Your result is too low!',
                                limit=-999))
        self.assertEqual(response.context['similar_results'], {
            'better_result': {
                'result': Result.objects.get(limit=10),
                'answers': [Answer.objects.get(pk=1), Answer.objects.get(pk=14)]
            },
            'worse_result': None
        })

    def testTestWithWorseSimilarResults(self):
        self.client.get(reverse('tests:view', args=(1,)))

        session = self.client.session
        session['test_status'] = 'finished'
        session['answers'] = {
            'question_1': ['1', '3'],
            'question_2': ['5', '6'],
            'question_3': ['8', '9'],
            'question_4': ['12'],
            'question_5': ['13', '14'],
            'question_6': ['15', '16', '20'],
            'question_7': ['21', '23'],
            'question_8': ['24'],
        }
        session.save()

        response = self.client.get(reverse('tests:result', args=(1,)))

        self.assertEqual(response.context['score'], 44)
        self.assertEqual(response.context['result'],
                         Result.objects.get(limit=30))
        self.assertEqual(response.context['similar_results'], {
            'better_result': None,
            'worse_result': {
                'result': Result.objects.get(limit=20),
                'answers': [Answer.objects.get(pk=17)]
            }
        })

    def testSimilarResultsOtherAnswers(self):
        self.client.get(reverse('tests:view', args=(1,)))

        session = self.client.session
        session['test_status'] = 'finished'
        session['answers'] = {
            'question_1': ['1', '4'],
            'question_2': ['5'],
            'question_3': ['9'],
            'question_4': ['12'],
            'question_5': ['13'],
            'question_6': ['15', '16'],
            'question_7': ['23'],
            'question_8': ['24'],
        }
        session.save()

        response = self.client.get(reverse('tests:result', args=(1,)))

        answers = ['1', '4', '5', '9', '12', '13', '15', '16', '23', '24']

        for answer in response.context['similar_results']['better_result']['answers']:
            self.assertNotIn(answer.pk, answers)

        for answer in response.context['similar_results']['worse_result']['answers']:
            self.assertNotIn(answer.pk, answers)

    def testSimilarResultsDifferentPages(self):
        self.client.get(reverse('tests:view', args=(1,)))

        session = self.client.session
        session['test_status'] = 'finished'
        session['answers'] = {
            'question_1': ['1', '4'],
            'question_2': ['5'],
            'question_3': ['9'],
            'question_4': ['12'],
            'question_5': ['13'],
            'question_6': ['15', '16'],
            'question_7': ['23'],
            'question_8': ['24'],
        }
        session.save()

        response = self.client.get(reverse('tests:result', args=(1,)))

        pages = []
        for answer in response.context['similar_results']['better_result']['answers']:
            self.assertNotIn(answer.question.page, pages)
            pages.append(answer.question.page)

        pages = []
        for answer in response.context['similar_results']['worse_result']['answers']:
            self.assertNotIn(answer.question.page, pages)
            pages.append(answer.question.page)
