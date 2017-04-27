from unittest import TestCase
from mock import patch, Mock, MagicMock
from livesync.fswatcher import BaseEventHandler
from livesync.core.handler import LiveReloadRequestHandler


class BaseEventHandlerTestCase(TestCase):
    def setUp(self):
        self.handler = BaseEventHandler()
        self.mock_event = MagicMock(src_path='/path/file', dest_path='/path/newfile')

        self.getmd5_patcher = patch('livesync.fswatcher.handlers.get_md5', return_value='md5hash')
        self.mock_get_md5 = self.getmd5_patcher.start()

        self.handle_patcher = patch.object(self.handler, 'handle')
        self.mock_handle = self.handle_patcher.start()

    def tearDown(self):
        self.getmd5_patcher.stop()
        self.handle_patcher.stop()

    def test_on_deleted_remove_file_from_history(self):
        self.handler.history[self.mock_event.src_path] = "md5hash"
        # act
        self.handler.on_deleted(self.mock_event)
        # assert
        self.assertNotIn(self.mock_event.src_path, self.handler.history)

    def test_on_deleted_invokes_handle(self):
        self.handler.history[self.mock_event.src_path] = "md5hash"
        # act
        self.handler.on_deleted(self.mock_event)
        # assert
        self.mock_handle.assert_called_with(self.mock_event)

    def test_on_moved_updates_history(self):
        self.handler.history[self.mock_event.src_path] = "md5hash"
        # act
        self.handler.on_moved(self.mock_event)
        # assert
        self.assertNotIn(self.mock_event.src_path, self.handler.history)
        self.assertIn(self.mock_event.dest_path, self.handler.history)
        self.assertEqual(self.handler.history[self.mock_event.dest_path], 'md5hash')

    def test_on_moved_adds_to_history(self):
        # act
        self.handler.on_moved(self.mock_event)
        # assert
        self.assertIn(self.mock_event.dest_path, self.handler.history)
        self.assertEqual(self.handler.history[self.mock_event.dest_path], 'md5hash')

    def test_on_moved_invokes_handle(self):
        self.handler.history[self.mock_event.src_path] = "md5hash"
        # act
        self.handler.on_moved(self.mock_event)
        # assert
        self.mock_handle.assert_called_with(self.mock_event)

    def test_on_modified_adds_to_history(self):
        # act
        self.handler.on_modified(self.mock_event)
        # assert
        self.assertIn(self.mock_event.src_path, self.handler.history)
        self.assertEqual(self.handler.history[self.mock_event.src_path], 'md5hash')

    def test_on_modified_invoked_handle(self):
        # act
        self.handler.on_modified(self.mock_event)
        # assert
        self.mock_handle.assert_called_with(self.mock_event)

    def test_on_modified_ignores_unchanged_files(self):
        self.handler.history[self.mock_event.src_path] = "md5hash"
        #act
        self.handler.on_modified(self.mock_event)
        # assert
        self.mock_handle.assert_not_called()

class LiveReloadEventHandlerTestCase(TestCase):
    def setUp(self):
        self.handler = LiveReloadRequestHandler()

    @patch('livesync.asyncserver.dispatcher.dispatch')
    def test_handle_dispatches_refresh(self, mock_dispatch):
        self.handler.handle(Mock())

        mock_dispatch.assert_called_with('refresh')
