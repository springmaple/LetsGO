import os
import subprocess

from PIL import Image

import util
from settings import Settings


class Company:
    def __init__(self, company_code):
        self.company_code = company_code


class Item:
    def __init__(self, code, desc):
        self.code = code
        self.desc = desc


_tmp_dir = 'C:\\Users\\wilson.ong\\Desktop\\'


class ViewModel:
    def __init__(self, fs, st, settings: Settings):
        self._fs = fs
        self._st = st
        self._settings = settings
        self.companies = [Company(data) for data in settings.list_company_codes()]
        self.items = []

    def set_company_code(self, company_code: str):
        self._company_code = company_code

    def load_items(self):
        self.items = [Item(doc.get('code'), doc.get('description')) for doc in
                      self._fs.collection(f'data/{self._company_code}/items').stream()]

    def save_image(self, item_code: str, filename: str):
        converted = _to_webp(filename)
        blob = self._st.blob(f'{self._company_code}/{util.esc_key(item_code)}.webp')
        blob.upload_from_filename(filename=converted)

    def get_image(self, item_code: str):
        key = util.esc_key(item_code)
        blob = self._st.get_blob(f'{self._company_code}/{key}.webp')
        if not blob:
            return None
        image_path = os.path.join(_tmp_dir, 'dl.webp')
        blob.download_to_filename(image_path)
        return _to_png(image_path)


def _to_png(filename: str):
    dwebp = os.path.join(_get_webp_dir(), 'dwebp.exe')
    out = os.path.join(_tmp_dir, 'out.png')
    subprocess.call([dwebp, filename, '-o', out], cwd=_get_webp_dir())
    return out


def _to_webp(filename: str):
    image = Image.open(filename)
    width, height = _resize_image(*image.size)
    prog = os.path.join(_get_webp_dir(), 'cwebp.exe')
    out = os.path.join(_tmp_dir, 'out.webp')
    subprocess.call([prog, filename,
                     '-o', out,
                     '-m', '6',
                     '-resize', str(width), str(height),
                     '-jpeg_like'], cwd=_get_webp_dir())
    return out


def _resize_image(width, height, max_size=800):
    x, y, is_swap = (width, height, False) if width > height else (height, width, True)
    if x > max_size:
        ratio = max_size // width
        x = max_size
        y = int(y * ratio)
        width, height = (x, y) if not is_swap else (y, x)
    return width, height


def _get_webp_dir():
    folder = os.path.join(os.path.dirname(__file__), '..\\..\\res\\webp\\')
    return os.path.abspath(folder)
