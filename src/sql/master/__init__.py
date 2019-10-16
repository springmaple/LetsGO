import datetime
import decimal
import json


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
        val = self._data.FindField(field_name).AsString
        dt_obj = datetime.datetime.strptime(str(val), '%d/%m/%Y')
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


class Keywords:
    def __init__(self, *original_texts):
        self._original_texts = original_texts

    def to_index(self):
        index = set()
        for original_text in self._original_texts:
            index = index.union(self._build_index(original_text))
        return list(index)

    def _build_index(self, text: str):
        text = text.lower()
        index = set()
        text_len = len(text)
        i = text_len
        while i > 0:
            j = 0
            while (j + i) <= text_len:
                index.add(text[j:j + i])
                j += 1
            i -= 1

        return index
