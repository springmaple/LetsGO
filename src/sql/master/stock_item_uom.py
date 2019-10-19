from sql.entity import Entity


class StockItemUom(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.code = self._get_str('Code')  # Primary Key
        self.uom = self._get_str('UOM')  # Primary Key
        self.rate = self._get_decimal('Rate')
        self.ref_cost = self._get_currency('RefCost')
        self.min_cost = self._get_currency('MinCost')
        self.max_cost = self._get_currency('MaxCost')
        self.ref_price = self._get_currency('RefPrice')
        self.min_price = self._get_currency('MinPrice')
        self.max_price = self._get_currency('MaxPrice')
        self.is_base = self._get_bool('IsBase')
