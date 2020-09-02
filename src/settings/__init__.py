import json
from typing import List

from server import util, Profile

_FILE_NAME = 'settings.json'


class Settings:
    def __init__(self):
        self._settings_file = util.find_file(_FILE_NAME)
        with open(self._settings_file, mode='r') as f:
            self._settings = json.load(f)

    def list_profiles(self) -> List[Profile]:
        return [Profile(profile) for profile in self._settings['profiles']]

    def get_profile(self, company_code: str) -> Profile:
        for profile in self.list_profiles():
            if profile.company_code == company_code:
                return profile
        raise Exception(f'Profile for "{company_code}" not found.')

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
