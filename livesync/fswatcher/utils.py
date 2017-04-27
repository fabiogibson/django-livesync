import hashlib


def get_md5(fname):
    hash_md5 = hashlib.md5()

    with open(fname, "rb") as rfile:
        for chunk in iter(lambda: rfile.read(4096), b""):
            hash_md5.update(chunk)

        return hash_md5.hexdigest()
