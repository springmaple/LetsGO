class BaseObject:
    def to_dict(self):
        attrs = vars(self)
        return {key: val for key, val in attrs.items() if not key.startswith('_')}


class Profile(BaseObject):
    def __init__(self, data):
        self.company_code = data['company_code']
        self.company_name = data['company_name']
