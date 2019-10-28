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

    def get_prop(self, company_code: str, prop_name: str) -> int:
        for profile in self._settings['profiles']:
            if profile['company_code'] == company_code:
                if prop_name in profile:
                    return profile[prop_name]
                break
        return 0

    def set_prop(self, company_code: str, prop_name: str, timestamp: int):
        for profile in self._settings['profiles']:
            if profile['company_code'] == company_code:
                profile[prop_name] = timestamp
                self._save()
                return

    def _save(self):
        data = json.dumps(self._settings, indent=2)
        with open(self._settings_file, mode='w') as f:
            print(data, file=f)
