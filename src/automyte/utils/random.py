import hashlib
import uuid


def random_hash(of: str | None = None):
    hash_from = of.encode() if of else uuid.uuid4().bytes
    return hashlib.md5(hash_from).hexdigest()
