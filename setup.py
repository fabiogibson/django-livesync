import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-livesync',
    version='0.5',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='TODO',
    long_description=README,
    url='',
    author='Fabio Gibson',
    author_email='fabiogibson.rj@gmail.com',
    install_requires=['watchdog>=0.8.3', 'tornado==4.5.1', 'websocket-client>=0.40.0',],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
