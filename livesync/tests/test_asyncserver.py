import unittest
import json
import time
from mock import Mock, patch
from livesync.asyncserver import WebsocketServer
from multiprocessing import Process
from websocket import create_connection
from livesync.asyncserver.handler import Hub
from livesync.asyncserver import dispatcher
from django.conf import settings


class AsyncServerTestCase(unittest.TestCase):

    def setUp(self):
        self.server = WebsocketServer()
        self.process = Process(target=self.server.run_forever)
        self.process.start()
        self.connections = set()

    def tearDown(self):
        self.server.server_close()
        self.process.terminate()
        self.process.join(timeout=0.5)

        for connection in self.connections:
            connection.close()

    def connect(self):
        connection = create_connection("ws://127.0.0.1:9001")
        self.connections.add(connection)
        return connection

    def test_dispatcher(self):
        client = self.connect()
        # act
        dispatcher.dispatch('refresh')
        # assert
        self.assertEqual(json.dumps(dispatcher.EVENTS['refresh']), client.recv())

    @patch('livesync.asyncserver.dispatcher.dispatch')
    def test_dispatcher_async(self, mock_dispatch):
        # act
        dispatcher.dispatch_async('refresh')
        # ugly wait for the message to be echoed :(
        time.sleep(1)
        # assert
        mock_dispatch.assert_called_with('refresh')

class HubTestCase(unittest.TestCase):
    def tearDown(self):
        Hub.clients.clear()

    def test_register_client(self):
        # act
        Hub.register(1)
        # asert
        self.assertIn(1, Hub.clients)
        self.assertEquals(1, len(Hub.clients))

    def test_remove_client(self):
        # mock
        Hub.clients = set([1])
        # act
        Hub.remove(1)
        # assert
        self.assertNotIn(1, Hub.clients)

    def test_echo_to_registered_clients(self):
        # mock
        client_a = Mock()
        client_b = Mock()
        Hub.clients = set([client_a, client_b])
        # act
        Hub.echo(client_a, 'message to be echoed')
        # assert
        client_b.send_text.assert_called()
        client_a.send_text.assert_not_called()
