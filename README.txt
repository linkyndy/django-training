=====
Tests
=====

Tests is a simple Django app to conduct Web-based multiple-answer tests.

Quick start
-----------

1. Add "tests" to your INSTALLED_APPS settings like this::

		INSTALLED_APPS = (
			...
			'tests',
		)

2. Include the tests URLconf in your project urls.py like this::

		url(r'^tests/', include('tests.urls')),

3. Run `python manage.py syncdb` to create the tests models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a test (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/tests/ to participate in the test.
