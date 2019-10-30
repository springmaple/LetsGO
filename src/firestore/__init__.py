import firebase_admin
from firebase_admin import credentials, firestore, storage

import util


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
        file = util.find_file('service-account.json')
        cred = credentials.Certificate(file)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'yotime-2019.appspot.com'
        })
        _is_firebase_initialized = True
