import sys
from livesync.asyncserver.handler import WebSocketHandler

if sys.version_info[0] < 3:
    from SocketServer import ThreadingMixIn, TCPServer
else:
    from socketserver import ThreadingMixIn, TCPServer


class WebsocketServer(ThreadingMixIn, TCPServer):
    """
	A websocket server waiting for clients to connect.

    Args:
        port(int): Port to bind to
        host(str): Hostname or IP to listen for connections. By default 127.0.0.1
            is being used. To accept connections from any client, you should use
            0.0.0.0.
        loglevel: Logging level from logging module to use for logging. By default
            warnings and errors are being logged.

    Properties:
        clients(list): A list of connected clients. A client is a dictionary
            like below.
                {
                 'id'      : id,
                 'handler' : handler,
                 'address' : (addr, port)
                }
    """
    allow_reuse_address = True
    daemon_threads = True  # comment to keep threads alive until finished

    def __init__(self, port=9001, host='127.0.0.1'):
        TCPServer.__init__(self, (host, port), WebSocketHandler)

    def run_forever(self):
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            self.server_close()
        except:
            exit(1)
