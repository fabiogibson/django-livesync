import uuid
import tornado.testing
import tornado.ioloop
from livesync.asyncserver.server import LiveSyncSocketHandler, LiveSyncSocketServer
from livesync.asyncserver.handler import Hub
from livesync.asyncserver.dispatcher import dispatch


class AsyncServerTestCase(tornado.testing.AsyncTestCase):
    def connect(self, session_id=None, client_id=None):
        base_url = 'ws://localhost:{}/?'.format(self.port)
        if session_id:
            base_url += '&session_id={}'.format(session_id)
        if client_id:
            base_url += '&client_id={}'.format(client_id)
        return tornado.websocket.websocket_connect(base_url)

    def setUp(self):
        super(AsyncServerTestCase, self).setUp()
        self.app = LiveSyncSocketServer()
        server = tornado.httpserver.HTTPServer(self.app)
        socket, self.port = tornado.testing.bind_unused_port()
        server.add_socket(socket)

    def tearDown(self):
        tornado.ioloop.IOLoop.instance().stop()

    @tornado.testing.gen_test
    def test_client_receives_welcome_message(self):
        # act
        client = yield self.connect()
        response = yield client.read_message()
        # assert
        self.assertIn('welcome', response)

    @tornado.testing.gen_test
    def test_client_receives_rejoin_message(self):
        # act
        client = yield self.connect(LiveSyncSocketHandler.session_id, str(uuid.uuid4()))
        response = yield client.read_message()
        # assert
        self.assertIn('rejoin', response)

    @tornado.testing.gen_test
    def test_client_gets_registered_in_hub(self):
        # act
        client_id = uuid.uuid4()
        client = yield self.connect(client_id=client_id)
        # assert
        self.assertIn(str(client_id), Hub.clients())

    @tornado.testing.gen_test
    def test_client_gets_removed_from_hub(self):
        # act
        client_id = uuid.uuid4()
        client = yield self.connect(client_id=client_id)
        client.close()
        yield tornado.gen.sleep(0.1)
        # assert
        self.assertNotIn(str(client_id), Hub.clients())

    @tornado.testing.gen_test
    def test_handler_asks_hub_to_echo_messages(self):
        # act
        client_a = yield self.connect()
        client_b = yield self.connect()

        # discarding handshake
        yield client_b.read_message()

        client_a.write_message('{ "action": "test" }')
        message = yield client_b.read_message()

        # assert
        self.assertEqual('{ "action": "test" }', message)

    @tornado.testing.gen_test
    def test_redirect_action_updates_current_url(self):
        # act
        new_url = "http://url/"
        client = yield self.connect()
        client.write_message('{ "action": "redirect", "url": "%s"}' % new_url)

        yield tornado.gen.sleep(0.1)
        # assert
        self.assertEqual(LiveSyncSocketHandler.current_url, new_url)

    @tornado.testing.gen_test
    def test_server_close(self):
        self.app.start()
        # act
        self.app.server_close()
        # assert
        self.assertFalse(tornado.ioloop.IOLoop.initialized())
