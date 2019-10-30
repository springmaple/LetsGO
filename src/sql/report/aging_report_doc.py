from decimal import Decimal

from sql.entity import Entity


class AgingReportDoc(Entity):
    def __init__(self, data, customers):
        super().__init__(data)
        self.customer_code = self._get_str('Code')
        self.company_name = customers.get(self.customer_code, '')
        self.doc_type = self._get_str('DocType')
        self.doc_key = self._get_str('DocKey')
        self.doc_code = self._get_str('DocNo')
        self.doc_description = self._get_str('Description')
        self.agent_code = self._get_str('Agent')
        self.area_code = self._get_str('Area')
        self.doc_date = self._get_date('DocDate')
        self.post_date = self._get_date('PostDate')
        self.trans_date = self._get_date('TransDate')
        self.due_date = self._get_date('DueDate')
        self.terms = self._get_str('Terms')
        self.currency_code = self._get_str('CurrencyCode')
        self.currency_rate = self._get_decimal('CurrencyRate')
        for i in range(1, 7):
            self.amount = self._get_currency(f'C{i}')
            if self.amount != Decimal(0):
                break
