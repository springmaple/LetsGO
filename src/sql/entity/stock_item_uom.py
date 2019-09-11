from sql.entity import Entity


class StockItemUom(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.code = self._get_str('Code')  # Primary Key
        self.uom = self._get_str('UOM')  # Primary Key
        self.rate = self._get_decimal('Rate')
        self.ref_cost = self._get_decimal('RefCost')
        self.min_cost = self._get_decimal('MinCost')
        self.max_cost = self._get_decimal('MaxCost')
        self.ref_price = self._get_decimal('RefPrice')
        self.min_price = self._get_decimal('MinPrice')
        self.max_price = self._get_decimal('MaxPrice')
        self.is_base = self._get_bool('IsBase')
