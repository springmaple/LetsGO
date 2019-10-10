import util
import json

_FILE_NAME = 'settings.json'
_KEY_COMPANY_CODE = 'company_code'
_KEY_LAST_SALES_ORDER = 'last_sales_order'


class Settings:
    def __init__(self):
        self._settings_file = util.find_file(_FILE_NAME)
        with open(self._settings_file, mode='r') as f:
            self._settings = json.load(f)

    def get_company_code(self) -> str:
        return self._settings[_KEY_COMPANY_CODE]

    def get_last_sales_order(self) -> int:
        if _KEY_LAST_SALES_ORDER in self._settings:
            return self._settings[_KEY_LAST_SALES_ORDER]
        return 0

    def set_last_sales_order(self, timestamp: int):
        self._settings[_KEY_LAST_SALES_ORDER] = timestamp

    def _save_settings(self):
        data = json.dumps(self._settings, indent=4)
        with open(self._settings_file, mode='w') as f:
            print(data, file=f)
