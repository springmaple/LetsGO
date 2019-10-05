from sql.master import Entity


class Customer(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.code = self._get_str('Code')  # Primary key
        self.company_name = self._get_str('CompanyName')
        self.area = self._get_str('Area')
        self.agent = self._get_str('Agent')
        self.credit_terms = self._get_str('CreditTerm')
        self.currency_code = self._get_str('CurrencyCode')
        self.branch = []
