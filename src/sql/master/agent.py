from sql.master import Entity


class Agent(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.code = self._get_str('Code')  # Primary key
        self.description = self._get_str('Description')
        self.is_active = self._get_bool('IsActive')
