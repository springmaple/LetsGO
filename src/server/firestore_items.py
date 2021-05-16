import json
import os

from constants import TMP_DIR
from firestore import get_firestore_instance


class FirestoreItems:
    def __init__(self, company_code):
        self.company_code = company_code
        self.fs = get_firestore_instance()

    def get_items(self):
        """Get stock items from Firestore."""
        cache = self._get_cache_items_path()
        if os.path.exists(cache):
            with open(cache, mode='r') as f:
                return json.load(f)
        return self._download_cache_items()

    def delete_cache(self):
        cache = self._get_cache_items_path()
        if os.path.exists(cache):
            os.unlink(cache)

    def update_cache(self):
        self._download_cache_items()

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
