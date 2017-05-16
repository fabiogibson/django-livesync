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
        self.assertEqual(self.command.livehost, 'localhost')

    def test_parse_custom_port_and_host(self):
        options = {'liveport': 8888, 'addrport': '0.0.0.0:8000'}
        self.command._parse_options(**options)

        self.assertEqual(self.command.liveport, 8888)
        self.assertEqual(self.command.livehost, '0.0.0.0')

    def test_parse_invalid_port_raises_command_error(self):
        options = {'liveport': 'abc', 'addrport': ''}

        with self.assertRaises(CommandError):
            self.command._parse_options(**options)
