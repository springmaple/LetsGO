from flask import Flask, request, jsonify

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


@app.route('/sync_sql_acc')
def sync_sql_acc():
    request.args.get('company_code')
