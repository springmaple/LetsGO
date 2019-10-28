from sql.entity import Entity


class StockTrans(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.trans_no = self._get_int('TransNo')  # Primary key
        self.item_code = self._get_str('ItemCode')
