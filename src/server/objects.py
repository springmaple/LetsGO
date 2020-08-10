class BaseObject:
    def to_dict(self):
        attrs = vars(self)
        return {key: val for key, val in attrs.items() if not key.startswith('_')}


class Profile(BaseObject):
    def __init__(self, data):
        self.company_code = data['company_code']
        self.company_name = data['company_name']


class Item(BaseObject):
    def __init__(self, data):
        self.code = data['code']
        self.desc = data['description']
        self.created_on = data['created_on']
        self.quantity = data['quantity']
        self.stock_group_code = data['stock_group_code']
