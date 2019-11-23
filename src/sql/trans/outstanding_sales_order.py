from sql.entity import Entity


class OutstandingSalesOrder(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.doc_key = self._get_int('DocKey')
        self.doc_code = self._get_str('DocNo')
