from sql.entity import Entity


class StockItemGroup(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.code = self._get_str('Code')  # Primary Key
        self.description = self._get_str('Description')
        self.is_active = self._get_bool('IsActive')
        self.last_modified = self._get_int('LastModified')
