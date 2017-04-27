def encode_to_UTF8(data): # pragma: no cover
    try:
        return data.encode('UTF-8')
    except UnicodeEncodeError:
        return False


def try_decode_UTF8(data): # pragma: no cover
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return False
