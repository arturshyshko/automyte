import hashlib
import uuid


def random_hash():
    return hashlib.md5(uuid.uuid4().bytes).hexdigest()
