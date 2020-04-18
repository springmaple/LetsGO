class Profile:
    def __init__(self, data):
        self.company_code = data['company_code']
        self.company_name = data['company_name']


class Item:
    def __init__(self, data):
        self.code = data['code']
        self.desc = data['description']
        self.keywords = data['keywords']
