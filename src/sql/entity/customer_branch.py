from sql.entity import Entity


class CustomerBranch(Entity):
    def __init__(self, data):
        super().__init__(data)
        self.customer_code = self._get_str('Code')  # Primary Key
        self.name = self._get_str('BranchName')  # Primary Key
        self.location = [
            self._get_decimal('GeoLat'),
            self._get_decimal('GeoLong')
        ]
        self.address = [
            self._get_str('Address1'),
            self._get_str('Address2'),
            self._get_str('Address3'),
            self._get_str('Address4')
        ]
        self.phone = [
            self._get_str('Phone1'),
            self._get_str('Phone2')
        ]
        self.fax = [
            self._get_str('Fax1'),
            self._get_str('Fax2')
        ]
        self.email = self._get_str('Email')
