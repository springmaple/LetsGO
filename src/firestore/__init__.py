import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client


def get_firestore_instance() -> Client:
    cred = credentials.Certificate('../res/serviceAccount.json')
    firebase_admin.initialize_app(cred)
    return firestore.client()
