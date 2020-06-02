import firebase_admin
from firebase_admin import credentials, firestore, storage


def get_firebase_storage():
    _init_firebase()
    return storage.bucket()


def get_firestore_instance():
    _init_firebase()
    return firestore.client()


_is_firebase_initialized = False


def _init_firebase():
    global _is_firebase_initialized
    if not _is_firebase_initialized:
        from server import util
        file = util.find_file('service-account.json')
        cred = credentials.Certificate(file)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'letsgo-2019.appspot.com'
        })
        _is_firebase_initialized = True
