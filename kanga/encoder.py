import decimal
import json
import uuid
import datetime

import pandas as pd

from phonenumber_field.modelfields import PhoneNumber


class KangaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, PhoneNumber):
            return obj.as_e164
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, pd.Timestamp):
            return pd.Timestamp.isoformat()
        return super(KangaEncoder, self).default(obj)
