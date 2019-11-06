from sql.entity import Entity


class CompanyProfile(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.company_name = self._get_str('CompanyName')
