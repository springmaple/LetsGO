from sql.entity import Entity


class SalesOrder(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.doc_code = self._get_str('DocNo')
        self.is_cancelled = self._get_bool('Cancelled')
