from sql.entity import Entity


class AgingReportCustomer(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.customer_code = self._get_str('Code')
        self.company_name = self._get_str('CompanyName')
