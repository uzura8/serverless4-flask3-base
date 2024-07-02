import argparse
import boto3
import os
import sys
# from app.utils.log import init_logger
from app.utils.string import to_camel_case
from app.models.dynamodb import SiteConfig
from pprint import pprint


parent_dir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

allowed_tables = ['site_config']


class TableItemHandler:
    def __init__(self):
        self.allowed_tables = allowed_tables
        self.ddb_client = boto3.client('dynamodb')

    def __del__(self):
        pass

    def main(self, table, operation, id, attr, value, value_type):
        if not all([table, operation, id]):
            print('Error: Missing argument.')
            return

        if table not in self.allowed_tables:
            print(f"Error: Invalid table name '{table}'.")
            return

        # Generate class name from table name as PasscalCase
        class_name = ''.join(word.capitalize() for word in table.split('_'))
        # Get class object from class name using globals()
        model_class = globals()[class_name]

        id_name = self.get_id_name_by_table(table)
        keys = {id_name: id}
        item = model_class.get_one_by_pkey(keys, False, True)
        if not item:
            print(f"Error: No data related by '{keys}'.")
            return

        if operation == 'query':
            pprint(item)

        elif operation == 'update':
            if not attr:
                print('Error: Missing argument.')
                return

            vals = {attr: self.cast_val(value, value_type)}
            res = model_class.update(keys, vals, False, True)
            pprint(res)
        elif operation == 'delete':
            res = model_class.delete(keys)
            print('deleted')

    @staticmethod
    def get_id_name_by_table(table):
        if table in ['user']:
            return 'uid'
        prefix = to_camel_case(table)
        return f'{prefix}Id'

    @staticmethod
    def cast_val(val, val_type):
        if val_type == 'None' or val_type == 'null':
            return None
        elif val_type == 'str':
            return str(val)
        elif val_type == 'int':
            return int(val)
        elif val_type == 'bool':
            return bool(val)
        else:
            return str(val)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('table', choices=allowed_tables,
                        help="Choose the table")
    parser.add_argument('operation', choices=[
                        'query', 'update', 'delete'], help='Choose the operation')
    parser.add_argument('id', type=str, help='set primary id')
    parser.add_argument('--attr', '-a', required=False, type=str,
                        help='set attribute name to change')
    parser.add_argument('--value', '-v', required=False,
                        help='set value to change')
    parser.add_argument('--type', '-t', required=False, choices=['str', 'int', 'bool', 'None', 'null'],
                        default='str', help='set value type to change')
    args = parser.parse_args()

    handler = TableItemHandler()
    handler.main(args.table, args.operation, args.id,
                 args.attr, args.value, args.type)
