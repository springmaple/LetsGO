from queue import Queue
from threading import Lock

from server import util
from server.firestore_items import FirestoreItems
from server.objects import Profile, Item
from server.sql_acc_sync import SqlAccSynchronizer
from settings import Settings

event_queue = Queue()
lock = Lock()
sync_sql_thread = None


def get_profiles():
    """Get company profiles"""
    settings = Settings()
    return [profile.to_dict() for profile in settings.list_profiles()]


def get_items(code):
    """Get stock items"""
    items = FirestoreItems(code).get_items()
    return [item.to_dict() for item in items]

# @app.route('/get_photo')
# def get_photo():
#     company_code = request.args.get('company_code')
#     item_code = util.esc_key(request.args.get('item_code'))
#     storage = get_firebase_storage()
#     blob = storage.get_blob(f'{company_code}/{item_code}.webp')
#     if not blob:
#         return abort(404)
#     blob.download_to_filename(os.path.join(TMP_DIR, 'dl.webp'))
#     return get_file(TMP_DIR, 'dl.webp')
#
#
# @app.route('/set_photo')
# def set_photo():
#     pass
#
#
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
