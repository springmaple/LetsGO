import json
import os
import subprocess

from PIL import Image

from constants import TMP_DIR
from server import util
from settings import Settings


class Profile:
    def __init__(self, data):
        self.company_code = data['company_code']
        self.company_name = data['company_name']


class Item:
    def __init__(self, data):
        self.code = data['code']
        self.desc = data['description']
        self.keywords = data['keywords']


class ViewModel:
    def __init__(self, fs, st, settings: Settings):
        self._fs = fs
        self._st = st
        self._settings = settings

        self.profiles = [Profile(profile_data.to_dict()) for profile_data in settings.list_profiles()]
        self.current_profile = self.profiles[0]  # type: Profile
        self.items = self._get_items()

    def set_current_profile(self, profile: Profile):
        self.current_profile = profile
        self.items = self._get_items()

    def save_image(self, item_code: str, filename: str):
        converted = _to_webp(filename)
        blob = self._st.blob(f'{self._company_code()}/{util.esc_key(item_code)}.webp')
        blob.upload_from_filename(filename=converted)

    def get_image(self, item_code: str):
        key = util.esc_key(item_code)
        blob = self._st.get_blob(f'{self._company_code()}/{key}.webp')
        if not blob:
            return None
        image_path = os.path.join(TMP_DIR, 'dl.webp')
        blob.download_to_filename(image_path)
        return _to_png(image_path)

    def _company_code(self):
        return self.current_profile.company_code

    def _get_items(self, recovery_mode=False):
        cache = get_cache_items_path(self._company_code())
        if os.path.exists(cache):
            with open(cache, mode='r') as f:
                try:
                    items = json.load(f)
                    return [Item(item) for item in items]
                except:
                    if recovery_mode:
                        raise
            # auto recover from corrupted cache file.
            os.unlink(cache)
            return self._get_items(recovery_mode=True)

        list(download_cache_items(self._company_code(), self._fs))
        return self._get_items(recovery_mode)


def get_cache_items_path(company_code):
    return os.path.join(TMP_DIR, company_code, 'items.json')


def download_cache_items(company_code, fs):
    cache = get_cache_items_path(company_code)
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    data = []
    for doc in fs.collection(f'data/{company_code}/items').stream():
        item_dict = doc.to_dict()
        data.append(item_dict)
        yield item_dict
    with open(cache, mode='w') as f:
        json.dump(data, f)


def _to_png(filename: str):
    dwebp = os.path.join(_get_webp_dir(), 'dwebp.exe')
    out = os.path.join(TMP_DIR, 'out.png')
    subprocess.call([dwebp, filename, '-o', out], cwd=_get_webp_dir())
    return out


def _to_webp(filename: str):
    image = Image.open(filename)
    image.thumbnail((720, 720), Image.ANTIALIAS)
    width, height = image.size

    prog = os.path.join(_get_webp_dir(), 'cwebp.exe')
    out = os.path.join(TMP_DIR, 'out.webp')
    subprocess.call([prog, filename,
                     '-o', out,
                     '-m', '6',
                     '-resize', str(width), str(height),
                     '-jpeg_like'], cwd=_get_webp_dir())
    return out


def _get_webp_dir():
    folder = os.path.join(os.path.dirname(__file__), '..\\..\\res\\webp\\')
    return os.path.abspath(folder)
