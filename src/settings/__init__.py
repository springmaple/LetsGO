import json

import util
from sql import SqlCredential

_FILE_NAME = 'settings.json'


class Settings:
    def __init__(self):
        self._settings_file = util.find_file(_FILE_NAME)
        with open(self._settings_file, mode='r') as f:
            self._settings = json.load(f)

    def list_company_codes(self) -> list:
        return [profile['company_code'] for profile in self._settings['profiles']]

    def get_sql_credential(self, company_code: str) -> SqlCredential:
        for profile in self._settings['profiles']:
            if profile['company_code'] == company_code:
                return SqlCredential(
                    profile['sql_id'],
                    profile['sql_password'],
                    profile['sql_dcf'],
                    profile['sql_fdb']
                )

    def get_last_sales_order(self, company_code: str) -> int:
        for profile in self._settings['profiles']:
            if profile['company_code'] == company_code:
                if 'last_sales_order_timestamp' in profile:
                    return profile['last_sales_order_timestamp']
                break
        return 0

    def set_last_sales_order(self, company_code: str, timestamp: int):
        for profile in self._settings['profiles']:
            if profile['company_code'] == company_code:
                profile['last_sales_order_timestamp'] = timestamp
                return

    def save(self):
        data = json.dumps(self._settings, indent=2)
        with open(self._settings_file, mode='w') as f:
            print(data, file=f)
