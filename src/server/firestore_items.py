import json
import os

from constants import TMP_DIR
from firestore import get_firestore_instance


class FirestoreItems:
    def __init__(self, company_code):
        self.company_code = company_code
        self.fs = get_firestore_instance()

    def get_customers(self):
        """Get customers from Firestore."""
        return [doc.to_dict() for doc in self.fs.collection(f'data/{self.company_code}/customers').stream()]

    def get_items(self):
        """Get stock items from Firestore; results are cached."""
        cache = self._get_cache_items_path()
        if os.path.exists(cache):
            with open(cache, mode='r') as f:
                return json.load(f)
        return self._download_cache_items()

    def delete_cache(self):
        """Delete items cache."""
        cache = self._get_cache_items_path()
        if os.path.exists(cache):
            os.unlink(cache)

    def update_cache(self):
        """Update items cache."""
        self._download_cache_items()

    def set_settings(self, key, value):
        """Set settings."""
        settings_val = {key: value}
        self.fs.document(f'settings/{self.company_code}').set(settings_val)
        return settings_val[key]

    def get_settings(self, key):
        """Get settings."""
        settings_val = self.fs.document(f'settings/{self.company_code}').get([key])
        settings_val_dict = settings_val.to_dict()
        if key in settings_val_dict:
            return settings_val_dict[key]
        return None

    def _get_cache_items_path(self):
        return os.path.join(TMP_DIR, self.company_code, 'items.json')

    def _download_cache_items(self):
        cache = self._get_cache_items_path()
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        data_id = {}
        data = []
        for doc in self.fs.collection(f'data/{self.company_code}/items').stream():
            item_dict = doc.to_dict()
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
