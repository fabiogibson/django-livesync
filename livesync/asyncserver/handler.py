import re
import sys
import struct
from base64 import b64encode
from hashlib import sha1
from .utils import try_decode_UTF8, encode_to_UTF8
from .hub import Hub


if sys.version_info[0] < 3:
    from SocketServer import StreamRequestHandler
else:
    from socketserver import StreamRequestHandler


FIN    = 0x80
OPCODE = 0x0f
MASKED = 0x80
PAYLOAD_LEN = 0x7f
PAYLOAD_LEN_EXT16 = 0x7e
PAYLOAD_LEN_EXT64 = 0x7f

OPCODE_CONTINUATION = 0x0
OPCODE_TEXT = 0x1
OPCODE_BINARY = 0x2
OPCODE_CLOSE_CONN = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xA


class WebSocketHandler(StreamRequestHandler):
    def __init__(self, socket, addr, server):
        self.keep_alive = True
        self.valid_client = False
        self.handshake_done = False
        self.handlers = {
            OPCODE_TEXT: self.receive_message,
            OPCODE_PING: self.send_pong,
            OPCODE_PONG: self.receive_pong,
        }
        StreamRequestHandler.__init__(self, socket, addr, server)

    def handle(self):
        while self.keep_alive:
            if not self.handshake_done:
                self.handshake_done = handshake(self.request)
                self.valid_client = True
                Hub.register(self)
            elif self.valid_client:
                self.read_next_message()

    def read_next_message(self):
        try:
            b1, b2 = read_bytes(self.rfile, 2)
        except ValueError:
            b1, b2 = 0, 0

        opcode = b1 & OPCODE
        masked = b2 & MASKED
        payload_length = b2 & PAYLOAD_LEN

        if not b1 or opcode == OPCODE_CLOSE_CONN or not masked:
            self.keep_alive = 0
            return

        opcode_handler = self.handlers.get(opcode)
        decoded = decode_message(self.rfile, payload_length)
        opcode_handler(decoded)

    def receive_pong(self, msg):
        pass

    def receive_message(self, message):
        Hub.echo(sender=self, msg=message)

    def send_pong(self, message):
        self.send_text(message, OPCODE_PONG)

    def send_text(self, message, opcode=OPCODE_TEXT):
        """
        Important: Fragmented(=continuation) messages are not supported since
        their usage cases are limited - when we don't know the payload length.
        """
        payload = create_payload(message)

        if not payload:
            return

        header = create_header(len(payload), opcode)
        self.request.send(header + payload)

    def finish(self):
        Hub.remove(self)


def handshake(request):
    message = request.recv(1024).decode().strip()
    upgrade = re.search(r'\nupgrade[\s]*:[\s]*websocket', message.lower())

    if not upgrade:
        return False

    key = re.search(r'\n[sS]ec-[wW]eb[sS]ocket-[kK]ey[\s]*:[\s]*(.*)\r\n', message)

    if key:
        key = key.group(1)
    else:
        return False

    response = make_handshake_response(key)
    return request.send(response.encode())


def create_payload(message):
    # Validate message
    if isinstance(message, bytes):
        message = try_decode_UTF8(message)  # this is slower but ensures we have UTF-8
        if not message:
            return
    elif isinstance(message, str) or isinstance(message, unicode):
        pass
    else:
        return

    return encode_to_UTF8(message)


def create_header(payload_length, opcode):
    header = bytearray()
    header.append(FIN | opcode)

    # Normal payload
    if payload_length <= 125:
        header.append(payload_length)
    # Extended payload
    elif payload_length >= 126 and payload_length <= 65535:
        header.append(PAYLOAD_LEN_EXT16)
        header.extend(struct.pack(">H", payload_length))
    # Huge extended payload
    elif payload_length < 18446744073709551616:
        header.append(PAYLOAD_LEN_EXT64)
        header.extend(struct.pack(">Q", payload_length))
    else:
        raise Exception("Message is too big. Consider breaking it into chunks.")

    return header


def decode_message(rfile, payload_length):
    if payload_length == 126:
        payload_length = struct.unpack(">H", rfile.read(2))[0]

    elif payload_length == 127:
        payload_length = struct.unpack(">Q", rfile.read(8))[0]

    masks = read_bytes(rfile, 4)
    decoded = ""

    for char in read_bytes(rfile, payload_length):
        char ^= masks[len(decoded) % 4]
        decoded += chr(char)

    return decoded


def read_bytes(rfile, num):
    _bytes = rfile.read(num)
    return _bytes if sys.version_info[0] > 2 else [ord(b) for b in _bytes]


def make_handshake_response(key):
    return \
      'HTTP/1.1 101 Switching Protocols\r\n'\
      'Upgrade: websocket\r\n'              \
      'Connection: Upgrade\r\n'             \
      'Sec-WebSocket-Accept: %s\r\n'        \
      '\r\n' % calculate_response_key(key)


def calculate_response_key(key):
    uid = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    hash_key = sha1(key.encode() + uid.encode())
    response_key = b64encode(hash_key.digest()).strip()
    return response_key.decode('ASCII')
