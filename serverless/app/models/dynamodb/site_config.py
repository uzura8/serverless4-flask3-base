from boto3.dynamodb.conditions import Key
from app.models.dynamodb import Base
from app.utils.date import utc_iso


class SiteConfig(Base):
    table_name = 'site-config'

    public_attrs = []
    response_attrs = public_attrs + []
    private_attrs = []
    all_attrs = public_attrs + private_attrs

    @classmethod
    def get_val(self, name):
        item = self.get_one_by_name(name)
        return item['configVal'] if item else None

    @classmethod
    def get_one_by_name(self, name):
        table = self.get_table()
        res = table.query(
            KeyConditionExpression=Key('configName').eq(name)
        )
        return res['Items'][0] if 'Items' in res and res['Items'] else None

    @classmethod
    def save(self, name, val):
        time = utc_iso()
        table = self.get_table()
        item = self.get_one_by_name(name)
        if not item:
            item = {
                'configName': name,
                'configVal': val,
                'updatedAt': time,
            }
            table.put_item(Item=item)
            return item

        if item['configVal'] == val:
            return item

        table.update_item(
            Key={'configName': name},
            AttributeUpdates={
                'configVal': {
                    'Value': val
                },
                'updatedAt': {
                    'Value': time
                }
            },
        )
        return {
            'configName': name,
            'configVal': val,
            'updatedAt': time,
        }

    @classmethod
    def increament_number(self, name):
        item = self.get_one_by_name(name)
        if not item:
            self.save(name, 1)
            return 1

        table = self.get_table()
        # service_id_name = '#'.join([service_id, name])
        table.update_item(
            Key={'configName': name},
            UpdateExpression='ADD configVal :incr',
            ExpressionAttributeValues={':incr': 1}
        )
        return self.get_val(name)
