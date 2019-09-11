from sql.entity import Entity


class Customer(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.code = self._get_str('Code')  # Primary key
        self.company_name = self._get_str('CompanyName')
        self.branch = []
