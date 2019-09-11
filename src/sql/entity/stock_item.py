from sql.entity import Entity


class StockItem(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.doc_key = self._get_int('DocKey')  # Primary Key
        self.code = self._get_str('Code')
        self.description = self._get_str('Description')
        self.quantity = self._get_int('BalsQty')
        self.stock_group_code = self._get_str('StockGroup')
        self.is_active = self._get_bool('IsActive')
        self.created_on = self._get_date('CreationDate')
        self.last_modified = self._get_int('LastModified')
        self.uom = []
