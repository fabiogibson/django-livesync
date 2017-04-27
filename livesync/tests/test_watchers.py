from unittest import TestCase
from mock import patch, MagicMock, mock_open
from livesync.fswatcher import FileWatcher, utils


class FileWatcherTestCase(TestCase):
    def setUp(self):
        self.watcher = FileWatcher('.')

    def test_add_new_handler(self):
        # act
        self.watcher.add_handler(1)
        # assert
        self.assertIn(1, self.watcher.handlers)

    @patch('livesync.fswatcher.watcher.Observer.start')
    @patch('livesync.fswatcher.watcher.Observer.schedule')
    def test_start_watching(self, mock_schedule, mock_start):
        self.watcher.handlers = set([1])
        #act
        self.watcher.start()
        # assert
        mock_start.assert_called()
        mock_schedule.assert_called_with(1, '.', recursive=True)

    @patch('livesync.fswatcher.watcher.Observer.stop')
    def test_stop_watching(self, mock_stop):
        #act
        self.watcher.stop()
        # assert
        mock_stop.assert_called()


class UtilsTestCase(TestCase):
    def test_get_md5_from_file(self):
        with patch('livesync.fswatcher.utils.open', mock_open(read_data=b'file content'), create=True):
            # act
            result = utils.get_md5("/path/file")
            # assert
            self.assertEqual(result, 'd10b4c3ff123b26dc068d43a8bef2d23')
