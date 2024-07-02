import os
import boto3
from app.utils.date import utc_iso
from app.utils.string import new_uuid
from app.utils.survalog import calc_kill_ratio


class Base():
    __abstract__ = True

    IS_LOCAL = os.getenv('IS_LOCAL', 'False').lower() == 'true'
    PRJ_PREFIX = os.environ['PRJ_PREFIX']

    dynamodb = None
    reserved_values = None

    @classmethod
    def connect_dynamodb(self):
        if self.dynamodb:
            return self.dynamodb

        if self.IS_LOCAL:
            self.dynamodb = boto3.resource(
                'dynamodb', endpoint_url='http://localhost:8000')
        else:
            self.dynamodb = boto3.resource('dynamodb')
        return self.dynamodb

    @classmethod
    def get_table(self, table_name=None):
        dynamodb = self.connect_dynamodb()
        table_name = self.get_table_name()
        return dynamodb.Table(table_name)

    @classmethod
    def get_table_name(self):
        return '-'.join([self.PRJ_PREFIX, self.table_name])

    @classmethod
    def prj_exps_str(self, is_public=True):
        attrs = self.public_attrs if is_public else self.all_attrs
        res = [attr['key'] if isinstance(
            attr, dict) else attr for attr in attrs]
        return ', '.join(res)

    @classmethod
    def to_response(self, item):
        res = {}
        for i in self.response_attrs:
            if isinstance(i, str):
                k = i
                l = i
            if isinstance(i, dict):
                k = i['key']
                l = i['label']

            if k in item:
                val = item.get(k)
                if val is not None:
                    res[l] = val

        return res

    @classmethod
    def scan(self, options=None, is_return_raw=False):
        if options is None:
            options = {}
        table = self.get_table()
        res = table.scan(**options)

        if is_return_raw:
            return res

        return res.get('Items', [])

    @classmethod
    def scan_all(self):
        table = self.get_table()
        items = []
        params = {}
        while True:
            res = table.scan(**params)
            items.extend(res['Items'])
            if ('LastEvaluatedKey' in res):
                params['ExclusiveStartKey'] = res['LastEvaluatedKey']
            else:
                break
        return items

    @classmethod
    def get_all(self, keys, params=None, index=None, is_all_attrs=False, skey_cond_type='eq'):
        res = self.get_all_pager(
            keys, params, index, is_all_attrs, skey_cond_type)
        return res['items']

    @classmethod
    def get_all_pager(self, keys, params=None, index=None, is_all_attrs=False, skey_cond_type='eq'):
        """
        keys = {
            'pkey': 'pkey_value',
            'skey': 'skey_value',
        }
        params = {
            'order': 'asc' or 'desc',
            'count': number,
            'pagerKey': 'pagerKey_value',
        }
        """
        table = self.get_table()

        is_desc = False
        limit = 50
        if params:
            is_desc = params.get('order', 'asc') == 'desc'
            limit = params.get('count', 50)
        if limit > 200:
            limit = 200
        option = {
            'ScanIndexForward': not is_desc,
        }
        if limit:
            option['Limit'] = limit

        if params and params.get('pagerKey'):
            option['ExclusiveStartKey'] = params['pagerKey']

        # if projections:
        #     if isinstance(projections, list):
        #         projections = ', '.join(projections)
        #     option['ProjectionExpression'] = projections

        if index:
            option['IndexName'] = index

        if not isinstance(keys, dict) or len(keys) == 0:
            raise ModelInvalidParamsException("'pkey' is required on keys")

        key_items = list(keys.items())
        pkey, pval = key_items[0]
        key_cond_exps = ['#pk = :pk']
        exp_attr_names = {'#pk': pkey}
        exp_attr_vals = {':pk': pval}

        if len(key_items) > 1:
            skey, sval = key_items[1]
            exp_attr_names['#sk'] = skey
            exp_attr_vals[':sk'] = sval
            if skey_cond_type == 'begins_with':
                key_cond_exps.append('begins_with(#sk, :sk)')
            elif skey_cond_type in ['eq', 'lt', 'lte', 'gt', 'gte']:
                operator_map = {
                    'eq': '=',
                    'lt': '<',
                    'lte': '<=',
                    'gt': '>',
                    'gte': '>='
                }
                operator = operator_map[skey_cond_type]
                key_cond_exps.append(f'#sk {operator} :sk')
            else:
                raise ValueError(
                    f"Unsupported skey_cond_type: {skey_cond_type}")

        option['KeyConditionExpression'] = ' AND '.join(key_cond_exps)
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        res = table.query(**option)
        items = res.get('Items', [])
        return {
            'items': [self.to_response(item) for item in items] if not is_all_attrs else items,
            'hasNext': bool(res.get('LastEvaluatedKey')),
        }

    @classmethod
    def get_one(self, keys, index=None, is_all_attrs=False, is_desc=False):
        """
        keys = {
            'pkey': 'pkey_value',
            'skey': 'skey_value',
        }
        """
        params = {'count': 1}
        if is_desc:
            params['order'] = 'desc'
        items = self.get_all(keys, params, index, is_all_attrs)
        return items[0] if len(items) > 0 else None

    @classmethod
    def get_one_by_pkey(self, keys, consistent_read=False, is_all_attrs=False):
        table = self.get_table()
        get_item_kwargs = {
            'Key': keys
        }
        if consistent_read:
            get_item_kwargs['ConsistentRead'] = True

        res = table.get_item(**get_item_kwargs)
        item = res.get('Item')
        if not item:
            return None
        return item if is_all_attrs else self.to_response(item)

    @classmethod
    def delete(self, key_dict):
        table = self.get_table()
        res = table.delete_item(
            Key=key_dict
        )
        return res

    @classmethod
    def delete_table(self):
        table = self.get_table()
        res = table.delete()
        return res

    @classmethod
    def get_reserved_values(self, attr):
        if not self.reserved_values:
            return []

        if attr not in self.reserved_values:
            return []

        return self.reserved_values[attr]

    @classmethod
    def check_set_reserved_value(self, vals, is_raise_exp=True):
        if not self.reserved_values:
            return False

        for attr in self.reserved_values:
            if attr not in vals:
                continue

            if vals[attr] in self.reserved_values[attr]:
                if is_raise_exp:
                    raise ModelInvalidParamsException(
                        '%s value is not allowed' % attr)
                else:
                    return True

        return False

    @classmethod
    def create(self, vals, uuid_name=None, is_add_update_info=False):
        if not vals.get('createdAt'):
            if vals.get('updatedAt'):
                vals['createdAt'] = vals['updatedAt']
            else:
                vals['createdAt'] = utc_iso()

        if is_add_update_info:
            if not vals.get('updatedAt'):
                vals['updatedAt'] = vals['createdAt']
            if not vals.get('updatedBy') and vals.get('createdBy'):
                vals['updatedBy'] = vals['createdBy']

        self.check_set_reserved_value(vals)

        if uuid_name and (uuid_name not in vals or not vals.get(uuid_name)):
            vals[uuid_name] = new_uuid()

        table = self.get_table()
        table.put_item(Item=vals)
        return vals

    @classmethod
    def update(self, keys, vals, is_update_time=False, is_return_all_attrs=False):
        """
        keys = {
            'pkey': 'pkey_value',
        }
        """
        self.check_set_reserved_value(vals)
        table = self.get_table()

        if is_update_time:
            vals['updatedAt'] = utc_iso()

        update_attrs = {}
        for key, val in vals.items():
            update_attrs[key] = {'Value': val}

        table.update_item(
            Key=keys,
            AttributeUpdates=update_attrs,
        )
        return self.get_one_by_pkey(keys, True, is_return_all_attrs)

    @classmethod
    def update_by_conds(self, keys, upd_vals, cond_vals, is_update_time=False):
        self.check_set_reserved_value(upd_vals)
        table = self.get_table()

        if is_update_time:
            upd_vals['updatedAt'] = utc_iso()

        upd_exps = []
        exp_vals = {}
        for idx, (k, v) in enumerate(upd_vals.items()):
            upd_exps.append(f"{k} = :upd_val{idx}")
            exp_vals[f":upd_val{idx}"] = v

        upd_exps_str = "SET " + ", ".join(upd_exps)

        # set ConditionExpression
        cond_exps = []
        for idx, (k, v) in enumerate(cond_vals.items(), start=len(upd_vals)):
            cond_exps.append(f"{k} = :cond_val{idx}")
            exp_vals[f":cond_val{idx}"] = v

        cond_exps_str = " AND ".join(cond_exps)

        try:
            res = table.update_item(
                Key=keys,
                UpdateExpression=upd_exps_str,
                ConditionExpression=cond_exps_str,
                ExpressionAttributeValues=exp_vals
            )
            return self.get_one(keys)

        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            raise ModelConditionalCheckFailedException(
                "Condition not met, no action taken.")

    @classmethod
    def update_pk_value(self, current_keys, update_vals, is_update_time=False):
        item = self.get_one(current_keys, None, False)
        for attr, val in update_vals.items():
            item[attr] = val

        if is_update_time:
            item['updatedAt'] = utc_iso()

        self.delete(current_keys)
        return self.create(item)

    @classmethod
    def batch_get_items(self, keys):
        dynamodb = self.connect_dynamodb()
        table_name = self.get_table_name()
        res = dynamodb.batch_get_item(
            RequestItems={
                table_name: {
                    'Keys': keys,
                    'ConsistentRead': True
                }
            },
            ReturnConsumedCapacity='TOTAL'
        )
        return res['Responses'][table_name]

    @classmethod
    def batch_save(self, items, pkeys=None, is_overwrite=False):
        # If set overwrite_by_pkeys, the batch_writer will overwrite the item
        table = self.get_table()
        overwrite_by_pkeys = pkeys if is_overwrite and pkeys else []
        with table.batch_writer(overwrite_by_pkeys=overwrite_by_pkeys) as batch:
            for item in items:
                # target_keys = {k: v for k, v in item.items() if k in pkeys or not pkeys}
                target_keys = {k: v for k, v in item.items()}
                batch.put_item(target_keys)

    @classmethod
    def batch_delete(self, items):
        table = self.get_table()
        with table.batch_writer() as batch:
            for item in items:
                # target_keys = {k: v for k, v in item.items() if k in pkeys or not pkeys}
                target_keys = {k: v for k, v in item.items()}
                batch.delete_item(target_keys)

    @classmethod
    def truncate(self):
        table = self.get_table()
        delete_items = []
        params = {}
        while True:
            res = table.scan(**params)
            delete_items.extend(res['Items'])
            if ('LastEvaluatedKey' in res):
                params['ExclusiveStartKey'] = res['LastEvaluatedKey']
            else:
                break

        key_names = [x['AttributeName'] for x in table.key_schema]
        delete_keys = [{k: v for k, v in x.items() if k in key_names}
                       for x in delete_items]

        with table.batch_writer() as batch:
            for key in delete_keys:
                batch.delete_item(Key=key)

    @classmethod
    def update_add_values(self, keys, add_vals, is_return_updated_item=False):
        if all(x == 0 for x in add_vals.values()):
            return

        table = self.get_table()
        upd_exp = []
        upd_vals = {}
        for k, v in add_vals.items():
            upd_exp.append(f'{k} :{k}')
            upd_vals[f':{k}'] = v

        upd_exp_str = 'ADD ' + ', '.join(upd_exp)
        res = table.update_item(
            Key=keys,
            UpdateExpression=upd_exp_str,
            ExpressionAttributeValues=upd_vals
        )

        if is_return_updated_item:
            return self.get_one_by_pkey(keys, True, True)
        else:
            return res

    # For survalog methods

    @classmethod
    def update_kill_death_score(self, keys, add_vals):
        accepted_tables = ['user-event', 'user-gun', 'user-score',
                           'user-field', 'user', 'gun', 'field']
        if self.table_name not in accepted_tables:
            raise Exception('This method is only for %s' %
                            ', '.join(accepted_tables))

        if all(x == 0 for x in add_vals.values()):
            return

        res = self.update_add_values(keys, add_vals, True)
        if not res:
            return

        if add_vals.get('killCount') or add_vals.get('deathCount'):
            item = self.get_one_by_pkey(keys, True, True)
            kill_count = item.get('killCount', 0)
            death_count = item.get('deathCount', 0)
            new_kill_ratio = calc_kill_ratio(kill_count, death_count)
            self.update(keys, {'killRatio': new_kill_ratio})

        return res


class ModelInvalidParamsException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ModelConditionalCheckFailedException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
