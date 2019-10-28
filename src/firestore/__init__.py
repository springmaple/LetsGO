import firebase_admin
from firebase_admin import credentials, firestore

import util


def get_firestore_instance():
    file = util.find_file('service-account.json')
    cred = credentials.Certificate(file)
    firebase_admin.initialize_app(cred)
    return firestore.client()
