import sys
from tornado.web import Application
from tornado.ioloop import IOLoop
from .handler import LiveSyncSocketHandler
from .dispatcher import dispatch
from socket import error
import time


class LiveSyncSocketServer(Application):
    def __init__(self,port=9001):
        self.port = port
        super(LiveSyncSocketServer, self).__init__([(r"/", LiveSyncSocketHandler)])

    def server_close(self):
        IOLoop.instance().stop()
        IOLoop.clear_instance()

    def start(self, started_event=None):
        try:
            self.listen(self.port)
            if started_event:
                # inform the main thread the server could be started.
                started_event.set()
            IOLoop.instance().start()
        except KeyboardInterrupt:
            self.server_close()
            sys.exit(0)
        except error as err:
            if err.errno == 98:
                time.sleep(1)
                dispatch('refresh')
                sys.exit(0)
            else:
                sys.exit(1)
