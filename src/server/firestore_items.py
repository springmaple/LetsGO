import json
import os

from constants import TMP_DIR
from firestore import get_firestore_instance


class FirestoreItems:
    def __init__(self, company_code):
        self.company_code = company_code
        self.fs = get_firestore_instance()
        self.cache_items = CacheItems(self.company_code, self.fs)
        self.cache_customers = CacheCustomers(self.company_code, self.fs)

    def get_customers(self):
        """Get customers from Firestore."""
        return FirestoreItems._get_cache_data(self.cache_customers)

    def get_items(self):
        """Get stock items from Firestore; results are cached."""
        return FirestoreItems._get_cache_data(self.cache_items)

    def delete_cache(self):
        """Delete items cache."""
        cache_paths = [
            self.cache_items.get_cache_path(),
            self.cache_customers.get_cache_path()
        ]
        for cache_path in cache_paths:
            if os.path.exists(cache_path):
                os.unlink(cache_path)

    def update_cache(self):
        """Update items cache."""
        self.cache_items.download_cache()
        self.cache_customers.download_cache()

    def set_settings(self, key, value):
        """Set settings."""
        settings_val = {key: value}
        self.fs.document(f'settings/{self.company_code}').set(settings_val)
        return settings_val[key]

    def get_settings(self, key):
        """Get settings."""
        settings_val = self.fs.document(f'settings/{self.company_code}').get([key])
        settings_val_dict = settings_val.to_dict()
        if settings_val_dict and key in settings_val_dict:
            return settings_val_dict[key]
        return None

    @staticmethod
    def _get_cache_data(cache):
        cache_path = cache.get_cache_path()
        if os.path.exists(cache_path):
            try:
                with open(cache_path, mode='r') as f:
                    return json.load(f)
            except:  # Could be cache file corrupted
                pass
        return cache.download_cache()


class Cache:
    def __init__(self, company_code, fs):
        self.company_code = company_code
        self.fs = fs

    def get_cache_path(self):
        """Get cache file path"""

    def download_cache(self):
        """Download cache data into cache file"""


class CacheItems(Cache):

    def get_cache_path(self):
        return os.path.join(TMP_DIR, self.company_code, 'items.json')

    def download_cache(self):
        cache = self.get_cache_path()
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        data_id = {}
        data = []
        for doc in self.fs.collection(f'data/{self.company_code}/items').stream():
            item_dict = doc.to_dict()
            if 'keywords' in item_dict:
                del item_dict['keywords']
            item_dict['est_quantity'] = item_dict['quantity']
            data_id[doc.id] = item_dict
            data.append(item_dict)
        for doc in self.fs.collection(f'data/{self.company_code}/itemQuantities').stream():
            if doc.id in data_id:
                item_dict = data_id[doc.id]
                item_dict['est_quantity'] -= (doc.get('open') or 0)
        with open(cache, mode='w') as f:
            json.dump(data, f)
        return data


class CacheCustomers(Cache):

    def get_cache_path(self):
        return os.path.join(TMP_DIR, self.company_code, 'customers.json')

    def download_cache(self):
        cache = self.get_cache_path()
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        data = []
        for doc in self.fs.collection(f'data/{self.company_code}/customers').stream():
            customer_dict = doc.to_dict()
            if 'keywords' in customer_dict:
                del customer_dict['keywords']
            data.append(customer_dict)
        with open(cache, mode='w') as f:
            json.dump(data, f)
        return data
