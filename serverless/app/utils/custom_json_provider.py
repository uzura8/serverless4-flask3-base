from decimal import Decimal
from flask.json.provider import DefaultJSONProvider
from boto3.dynamodb.types import Binary


class CustomJsonProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if int(obj) == obj:
                return int(obj)
            return float(obj)
        if isinstance(obj, Binary):
            return obj.value
        if isinstance(obj, bytes):
            return obj.decode()
        if isinstance(obj, set):
            return list(obj)

        return super().default(obj)
