"""Runserver command with livereload"""
import re
from socket import error as SocketError
from multiprocessing import Process, Event
from django.conf import settings
from django.core.management.base import CommandError
from django.core.management.commands.runserver import naiveip_re
from livesync.asyncserver import LiveSyncSocketServer, dispatcher
from livesync.fswatcher import FileWatcher
from livesync.core.handler import LiveReloadRequestHandler


if 'django.contrib.staticfiles' in settings.INSTALLED_APPS:
    from django.contrib.staticfiles.management.commands.runserver import \
        Command as RunserverCommand
else:
    from django.core.management.commands.runserver import Command as RunserverCommand


class Command(RunserverCommand):
    """
    Command for running the development server with LiveSyncReload.
    """
    help = 'Starts a lightweight Web server for development with Live Sync.'

    def __init__(self):
        super(Command, self).__init__()
        self.server = None
        self.server_process = None
        self.file_watcher = None
        self.init_settings()

    def init_settings(self):
        if not hasattr(settings, 'DJANGO_LIVESYNC'):
            settings.DJANGO_LIVESYNC = dict()

        settings.DJANGO_LIVESYNC.setdefault('PORT', 9001)
        settings.DJANGO_LIVESYNC.setdefault('HOST', 'localhost')

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--liveport', action='store', dest='liveport', default=9001,
                            help='Host and port on which Django LiveSync shoud run.'),

    @property
    def liveport(self):
        return settings.DJANGO_LIVESYNC['PORT']

    @liveport.setter
    def liveport(self, value):
        settings.DJANGO_LIVESYNC['PORT'] = value

    @property
    def livehost(self):
        return settings.DJANGO_LIVESYNC['HOST']

    @livehost.setter
    def livehost(self, value):
        settings.DJANGO_LIVESYNC['HOST'] = value

    def _start_async_server(self):
        self.server = LiveSyncSocketServer(port=self.liveport)
        server_started_event = Event()
        self.server_process = Process(target=self.server.start, args=(server_started_event,))
        self.server_process.daemon = True
        self.server_process.start()
        server_started_event.wait(timeout=0.1)
        return server_started_event.is_set()

    def _stop_async_server(self):
        if self.server_process:
            self.server.server_close()
            self.server_process.join()

    def _start_watchdog(self):
        self.file_watcher = FileWatcher(settings.BASE_DIR)
        self.file_watcher.add_handler(LiveReloadRequestHandler())
        self.file_watcher.start()

    def _stop_watchdog(self):
        if self.file_watcher:
            self.file_watcher.stop()

    def _parse_options(self, **options):
        if options['liveport']:
            liveport = options['liveport']
            if not isinstance(liveport, int) and not liveport.isdigit():
                raise CommandError("LiveSync port must be an integer.")
            self.liveport = int(liveport)

        if options['addrport']:
            matches = re.match(naiveip_re, options['addrport'])
            if matches and matches.groups()[0]:
                self.livehost = matches.groups()[0]

    def stop_liveserver(self):
        self._stop_async_server()
        self._stop_watchdog()

    def start_liveserver(self, **options):
        self._parse_options(**options)

        if self._start_async_server():
            self._start_watchdog()

    def handle(self, *args, **options):
        self.start_liveserver(**options)
        super(Command, self).handle(*args, **options)
        self.stop_liveserver()
