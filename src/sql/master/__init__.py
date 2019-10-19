from sql.entity import Entity


class MasterMeta(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.total = self._get_int('Total')
