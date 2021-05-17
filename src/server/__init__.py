import base64
import os

from constants import TMP_DIR
from firestore import get_firebase_storage
from server import util
from server.firestore_items import FirestoreItems
from server.objects import Profile
from server.sql_acc_sync import SqlAccSynchronizer, _LAST_SYNC_SQL_TIMESTAMP
from server.util import esc_key, to_webp
from settings import Settings


def get_profiles():
    """Get company profiles"""
    settings = Settings()
    return [profile.to_dict() for profile in settings.list_profiles()]


def get_items(code):
    """Get stock items
    `code` is the company code."""
    return FirestoreItems(code).get_items()


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


def sync_sql_acc(code):
    sql_acc_synchronizer = SqlAccSynchronizer(code)
    try:
        yield from sql_acc_synchronizer.start_sync()

        yield {'type': 'update_cache', 'update_cache': 'Started!'}
        fs_items = FirestoreItems(code)
        fs_items.delete_cache()
        fs_items.update_cache()
        yield {'type': 'update_cache', 'update_cache': 'Completed!'}
    except Exception as ex:
        yield {'type': 'error', 'error': str(ex)}
    else:
        yield {'type': 'complete'}


def get_last_sync_sql_timestamp(code):
    settings = Settings()
    timestamp = settings.get_prop(code, _LAST_SYNC_SQL_TIMESTAMP)
    return {'timestamp': timestamp}  # return 0 if value is not set


def get_area_codes(code):
    areas = [item.get('area', None) for item in FirestoreItems(code).get_customers()]
    return sorted(list(filter(lambda area: area, set(areas))))
