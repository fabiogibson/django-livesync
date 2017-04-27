import unittest
from django.conf import settings
from django.core.management.base import CommandError
from livesync.management.commands.runserver import Command
from mock import patch


class OptionsParserTestcase(unittest.TestCase):
    def setUp(self):
        self.command = Command()

    def tearDown(self):
        settings.DJANGO_LIVESYNC = dict()

    def test_parse_default_options(self):
        options = {'liveport': None, 'addrport': ''}
        self.command._parse_options(**options)

        self.assertEqual(self.command.liveport, 9001)
        self.assertEqual(self.command.livehost, '127.0.0.1')

    def test_parse_custom_port_and_host(self):
        options = {'liveport': 8888, 'addrport': '0.0.0.0:8000'}
        self.command._parse_options(**options)

        self.assertEqual(self.command.liveport, 8888)
        self.assertEqual(self.command.livehost, '0.0.0.0')

    def test_parse_invalid_port_raises_command_error(self):
        options = {'liveport': 'abc', 'addrport': ''}

        with self.assertRaises(CommandError):
            self.command._parse_options(**options)

class RunServerCommandTestCase(unittest.TestCase):
    def setUp(self):
        self.command = Command()
        self.live_reload_patcher = patch('livesync.asyncserver.dispatcher.dispatch_async')
        self.mock_live_reload = self.live_reload_patcher.start()

    def tearDown(self):
        self.live_reload_patcher.stop()
        settings.DJANGO_LIVESYNC = dict()

        if self.command.server_process:
            self.command.server.server_close()

            while self.command.server_process.is_alive():
                self.command.server_process.terminate()
                self.command.server_process.join(timeout=0.5)

    def test_async_server_starts_only_on_first_run(self):
        # act
        first_call = self.command._start_async_server()
        second_call = self.command._start_async_server()
        # asser
        self.assertTrue(first_call)
        self.assertFalse(second_call)

    def test_async_server_first_run_does_not_request_live_reload(self):
        # act
        self.command._start_async_server()
        # assert
        self.mock_live_reload.assert_not_called()

    def test_async_server_second_run_requests_live_reload(self):
        # act
        self.command._start_async_server()
        self.command._start_async_server()
        # assert
        self.mock_live_reload.assert_called()

    def test_start_watch_dog(self):
        options = {'liveport': None, 'addrport': ''}
        # act
        self.command.start_liveserver(**options)
        # assert
        self.assertTrue(self.command.file_watcher.observer.is_alive())

    def test_stop_watch_dog(self):
        # mock
        with patch.object(self.command, 'file_watcher') as mock_watcher:
            # act
            self.command._stop_watchdog()
            # assert
            mock_watcher.stop.assert_called()

    def test_start_async_server(self):
        options = {'liveport': None, 'addrport': ''}
        # act
        self.command.start_liveserver(**options)
        # assert
        self.assertTrue(self.command.server_process.is_alive())

    def test_stop_async_server(self):
        # mock
        with patch.object(self.command, 'server') as mock_server, \
             patch.object(self.command, 'server_process') as mock_server_process:
             # act
            self.command._stop_async_server()
            # asert
            mock_server.server_close.assert_called()
            mock_server_process.join.assert_called()

    def test_stop_live_server(self):
        with patch.object(self.command, '_stop_watchdog') as mock_stop_watchdog, \
             patch.object(self.command, '_stop_async_server')  as mock_stop_async_server:
            self.command.stop_liveserver()
            mock_stop_watchdog.assert_called()
            mock_stop_async_server.assert_called()
