import uuid
import json
from tornado.websocket import WebSocketHandler
from .hub import Hub


class LiveSyncSocketHandler(WebSocketHandler):
    current_url = None
    session_id = uuid.uuid4()

    def __init__(self, *args, **kwargs):
        super(LiveSyncSocketHandler, self).__init__(*args, **kwargs)
        self.id = None

    def check_origin(self, origin):
        return True

    @property
    def url(self):
        return self.request.headers.get("Origin", "") + '/'

    def open(self):
        self.id = self.get_query_argument('client_id', uuid.uuid4())
        Hub.register(self)

        if str(self.session_id) != self.get_query_argument('session_id', None):
            self.write_message(json.dumps({
                'action': 'welcome',
                'payload':  {
                    'client_id': str(self.id),
                    'session_id': str(self.session_id),
                    'current_url': self.current_url,
                },
            }))
        else:
            self.write_message(json.dumps({
                'action': 'rejoin',
                'payload':  {},
            }))

        if not LiveSyncSocketHandler.current_url:
            LiveSyncSocketHandler.current_url = self.url

    def on_connection_close(self):
        Hub.remove(self.id)

    def on_message(self, message):
        message_json = json.loads(message)
        action = message_json.get('action')

        if action == "redirect":
            LiveSyncSocketHandler.current_url = message_json.get('url')

        Hub.echo(self.id, message)
