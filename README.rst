What's this project?
=================

It's a simple Django application which will automatically reload
your browser everytime Django Development Server is restarted and
a static file or django template changes. Besides this,
if you connect multiple browsers and devices on your development server,
these will be all synchronized.

Quick start guide
=================

Before installing, you'll need to have a copy of
`Django <http://www.djangoproject.com>`_ already installed. For the
current release, Django 1.8 or newer is required.

For further information, consult the `Django download page
<http://www.djangoproject.com/download/>`_, which offers convenient
packaged downloads and installation instructions.


Installing
--------------------

Automatic installation using PyPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

type::

    pip install django-livesync


Basic configuration and use
---------------------------

Once installed, you can add Django LiveSync to any Django-based
project you're working on. The default setup will enable the following features.

1. Every time django development server is reloaded, all connected browsers will automatically refresh.

2. Every time a static file or template is updated, all connected browsers will automatically refresh.

3. Your actions will be synchronized between all connected browsers and devices. Currently supports:

   * Page scroll.
   * Page reload.
   * Element click.
   * Form fields in general.

**IMPORTANT**: Currently, it was only tested against Google Chrome and Mozilla Firefox web browsers.


Configuration
--------------------

Installing the application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Begin by adding ``livesync`` to the ``INSTALLED_APPS`` setting of
your project. You can also specify the following additional settings:

``LIVE_PORT``
    This is the number of the port on which live server will run.


Setup Middleware
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add ``livesync.core.middleware.DjangoLiveSyncMiddleware`` to the ``MIDDLEWARE_CLASSES`` setting of your project.


**IMPORTANT NOTES**:

    1. If you have 'django.contrib.staticfiles' application installed, you must register 'django-livesync' before it, otherwise live server will not launch.

    2. Django LiveSync will only execute if DEBUG is set to True.

Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You might have something like the following in your Django settings file::

    DEBUG = True

    INSTALLED_APPS = (
        '...',
        'livesync',
        'django.contrib.staticfiles',
        '...',
    )

    DJANGO_LIVESYNC = {
    	'PORT': 9999 # this is optional and is default set to 9001.
    }

    MIDDLEWARE_CLASSES = (
        'livesync.core.middleware.DjangoLiveSyncMiddleware',
    )


Once you've done this, run ``python manage.py runserver`` as usual.
