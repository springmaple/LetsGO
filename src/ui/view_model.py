import json
import os
import subprocess

from PIL import Image

import util
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


_tmp_dir = 'C:\\Users\\wilson.ong\\Desktop\\'


class ViewModel:
    def __init__(self, fs, st, settings: Settings):
        self._fs = fs
        self._st = st
        self._settings = settings

        self.profiles = [Profile(profile_data) for profile_data in settings.list_profiles()]
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
        image_path = os.path.join(_tmp_dir, 'dl.webp')
        blob.download_to_filename(image_path)
        return _to_png(image_path)

    def _company_code(self):
        return self.current_profile.company_code

    def _get_items(self):
        cache = os.path.join(_tmp_dir, self._company_code(), 'items.json')
        if os.path.exists(cache):
            with open(cache, mode='r') as f:
                items = json.load(f)
                return [Item(item) for item in items]

        os.makedirs(os.path.dirname(cache))
        data = [doc.to_dict() for doc in self._fs.collection(f'data/{self._company_code()}/items').stream()]
        with open(cache, mode='w') as f:
            json.dump(data, f)
        return [Item(d) for d in data]


def _to_png(filename: str):
    dwebp = os.path.join(_get_webp_dir(), 'dwebp.exe')
    out = os.path.join(_tmp_dir, 'out.png')
    subprocess.call([dwebp, filename, '-o', out, '-scale', '480', '480'], cwd=_get_webp_dir())
    return out


def _to_webp(filename: str):
    image = Image.open(filename)
    width, height = image.size
    prog = os.path.join(_get_webp_dir(), 'cwebp.exe')
    out = os.path.join(_tmp_dir, 'out.webp')
    shorter_side = width if width < height else height
    final_size = 480 if shorter_side > 480 else shorter_side
    subprocess.call([prog, filename,
                     '-o', out,
                     '-m', '6',
                     '-crop', '0', '0', str(shorter_side), str(shorter_side),
                     '-resize', str(final_size), str(final_size),
                     '-jpeg_like'], cwd=_get_webp_dir())
    return out


def _get_webp_dir():
    folder = os.path.join(os.path.dirname(__file__), '..\\..\\res\\webp\\')
    return os.path.abspath(folder)
