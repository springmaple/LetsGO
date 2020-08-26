import base64
import os
from queue import Queue
from threading import Lock

from constants import TMP_DIR
from firestore import get_firebase_storage
from server import util
from server.firestore_items import FirestoreItems
from server.objects import Profile, Item
from server.sql_acc_sync import SqlAccSynchronizer
from server.util import esc_key, to_webp
from settings import Settings

event_queue = Queue()
lock = Lock()
sync_sql_thread = None


def get_profiles():
    """Get company profiles"""
    settings = Settings()
    return [profile.to_dict() for profile in settings.list_profiles()]


def get_items(code):
    """Get stock items
    `code` is the company code."""
    items = FirestoreItems(code).get_items()
    return [item.to_dict() for item in items]


def get_photo(code, item_code):
    """Get photo base64 string."""
    storage = get_firebase_storage()
    blob = storage.get_blob(f'{code}/{esc_key(item_code)}.webp')
    if not blob:
        return {'b64_photo': None}
    image_path = os.path.join(TMP_DIR, 'dl.webp')
    blob.download_to_filename(image_path)
    with open(image_path, mode='rb') as f:
        return {'b64_photo': str(base64.encodebytes(f.read()), 'utf-8')}


def set_photo(code, item_code, file):
    """Set photo"""
    storage = get_firebase_storage()
    converted = to_webp(file)
    blob = storage.blob(f'{code}/{util.esc_key(item_code)}.webp')
    blob.upload_from_filename(filename=converted)
    with open(converted, mode='rb') as f:
        return {'b64_photo': str(base64.encodebytes(f.read()), 'utf-8')}


def delete_photo(code, item_code):
    """Delete photo"""
    storage = get_firebase_storage()
    blob = storage.blob(f'{code}/{util.esc_key(item_code)}.webp')
    blob.delete()
    return {'b64_photo': None}

# @app.route('/sync_sql_acc')
# def sync_sql_acc():
#     global sync_sql_thread
#     with lock:
#         if sync_sql_thread and sync_sql_thread.is_alive():
#             return
#
#         company_code = request.args.get('company_code')
#         sql_acc_synchronizer = SqlAccSynchronizer(company_code)
#
#         def sync():
#             try:
#                 for data in sql_acc_synchronizer.start_sync():
#                     event_queue.put(('sync', data))
#                 FirestoreItems(company_code).delete_cache()
#             except Exception as ex:
#                 event_queue.put(('sync', {'type': 'error', 'data': str(ex)}))
#             else:
#                 event_queue.put(('sync', {'type': 'complete'}))
#
#         sync_sql_thread = Thread(target=sync)
#         sync_sql_thread.start()
#         return '', 204
