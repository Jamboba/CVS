import hashlib


def get_hash_for_path(path):
    """Хэшируем файл"""
    sha1 = hashlib.sha1()
    with open(path, 'rb') as f:
        file_bytes = f.read()
        while file_bytes:
            sha1.update(file_bytes)
            file_bytes = f.read()
    return sha1.hexdigest()
