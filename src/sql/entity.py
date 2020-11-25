import datetime
import decimal
import json
import re
import subprocess

from sql.keywords import Keywords


class DictEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) == datetime.date:
            return obj.strftime('%Y-%m-%d')
        if type(obj) == decimal.Decimal:
            return "0" if obj == decimal.Decimal(0) else str(obj)
        if type(obj) == Keywords:
            return obj.to_index()
        if isinstance(obj, Entity):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)


class Entity:
    def __init__(self, data):
        self._data = data
        self._date_format = None

    def _get_str(self, field_name):
        return self._data.FindField(field_name).AsString

    def _get_decimal(self, field_name) -> decimal.Decimal:
        return self._data.FindField(field_name).AsCurrency

    def _get_currency(self, field_name) -> decimal.Decimal:
        currency = self._get_decimal(field_name)
        return currency.quantize(decimal.Decimal('.01'))

    def _get_int(self, field_name):
        val = self._data.FindField(field_name).AsString
        try:
            return int(val)
        except ValueError:
            return None

    def _get_bool(self, field_name):
        val = self._data.FindField(field_name).AsString
        if str(val).upper() in ('T', '1'):
            return True
        if str(val).upper() in ('F', '0', 'NONE', ''):
            return False
        raise Exception(f'unknown boolean value {val}')

    def _get_date(self, field_name):
        if not self._date_format:
            self._date_format = guess_system_date_format()
        val = self._data.FindField(field_name).AsString
        dt_obj = datetime.datetime.strptime(str(val), self._date_format)
        return dt_obj.date()

    def to_dict(self):
        attrs = vars(self)
        vals = {key: val for key, val in attrs.items() if not key.startswith('_')}
        return json.loads(json.dumps(vals, cls=DictEncoder))

    def __str__(self):
        attrs = vars(self)
        return ', '.join("%s: %s" % item
                         for item in attrs.items()
                         if not item[0].startswith('_'))


def guess_system_date_format():
    """https://superuser.com/a/951984"""
    output = subprocess.check_output(['reg', 'query', r'HKCU\Control Panel\International', '-v', 'sShortDate'])
    output = output.decode()
    for line in output.splitlines():
        partitions = line.split()
        if len(partitions) == 3 and partitions[0] == 'sShortDate':
            date_format = partitions[2]
            date_format = re.sub('d+', '%d', date_format, flags=re.IGNORECASE)
            date_format = re.sub('m+', '%m', date_format, flags=re.IGNORECASE)
            return re.sub('y+', '%Y', date_format, flags=re.IGNORECASE)
    return '%d/%m/%Y'
