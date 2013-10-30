from setuptools import setup


setup(
	name='Django Training Tests',
	version='0.1.0',
	author='Andrei Horak',
	author_email='andrei.horak@3pillarglobal.com',
	packages=['tests'],
	include_package_data=True,
	url='http://127.0.0.1:8000',
	license='LICENSE.txt',
	description='Tests is a simple Django app to conduct Web-based multiple-answer tests.',
	long_description=open('README.txt').read(),
    install_requires=['Django>=1.5'],
)
