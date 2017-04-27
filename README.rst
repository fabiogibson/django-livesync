Quick start guide
=================

Before installing, you'll need to have a copy of
`Django <http://www.djangoproject.com>`_ already installed. For the
current release, Django 1.10 or newer is required.

For further information, consult the `Django download page
<http://www.djangoproject.com/download/>`_, which offers convenient
packaged downloads and installation instructions.


Installing
--------------------

Automatic installation using PYPI.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

type::

    pip install django-livesync


Basic configuration and use
---------------------------

Once installed, you can add Django LiveSync to any Django-based
project you're working on. The default setup will enable the following features.

1. Automatic browser reload whenever development server restarts.
   Every time django development server is reloaded, all connected browsers will automatically refresh.

2. Automatic browser reload whenever a static file is updated.
   Every time a static file or template is updated, all connected browsers will automatically refresh.

3. Live syncronizathion between all connected browsers.
   Your actions will be syncronized between all connected browsers. Currently supports:
    Page scrolling.
    General clicks.
    Key presses.
    Browser refreshes.
    
**IMPORTANT**: Currently, it was tested against Google Chrome and Mozilla Firefox web browsers.


Configuration
--------------------

Begin by adding ``django-livesync`` to the ``INSTALLED_APPS`` setting of
your project. You can also specify the following additional settings:

``LIVE_PORT``
    This is the number of the port on which live asyncserver will run.

For example, you might have something like the following in your Django settings file::

    INSTALLED_APPS = (
        '...',
        'django-livesync'
    )

    DJANGO_LIVESYNC = {
    	'PORT': 9999 # default is set to 9001
    }


**IMPORTANT**: If you have 'django.contrib.staticfiles' application installed, you must register 'django-livesync' before it, otherwise livesync server will not be executed.

Once you've done this, run ``python manage.py runserver``.
