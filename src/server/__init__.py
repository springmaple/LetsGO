import os

from flask import Flask, request, jsonify, send_from_directory

from constants import TMP_DIR
from firestore import get_firebase_storage
from server import util
from server.firestore_items import FirestoreItems
from server.objects import Profile, Item
from settings import Settings

app = Flask(__name__)


@app.route('/')
def hello():
    return f'Hello, world!'


@app.route('/get_profiles')
def get_profiles():
    settings = Settings()
    return jsonify([Profile(profile_data) for profile_data in settings.list_profiles()])


@app.route('/get_items')
def get_items():
    company_code = request.args.get('company_code')
    return jsonify(FirestoreItems(company_code).get_items())


@app.route('/get_photo')
def get_photo():
    company_code = request.args.get('company_code')
    item_code = util.esc_key(request.args.get('item_code'))
    storage = get_firebase_storage()
    blob = storage.get_blob(f'{company_code}/{item_code}.webp')
    if not blob:
        return None
    blob.download_to_filename(os.path.join(TMP_DIR, 'dl.webp'))
    return get_file(TMP_DIR, 'dl.webp')


@app.route('/set_photo')
def set_photo():
    pass


@app.route('/sync_sql_acc')
def sync_sql_acc():
    request.args.get('company_code')


def get_file(directory, filename):
    response = send_from_directory(directory, filename, as_attachment=True)
    response.cache_control.max_age = 5  # seconds
    return response
