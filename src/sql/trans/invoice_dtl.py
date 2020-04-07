from sql.entity import Entity


class InvoiceDTL(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.from_doc_key = self._get_int('FromDocKey')
