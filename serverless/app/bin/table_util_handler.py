import boto3
import os
import sys
import argparse
# from app.utils.log import init_logger
from app.models.dynamodb import SiteConfig
from pprint import pprint


parent_dir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

allowed_tables = ['site_config']


class TableUtilHandler:
    def __init__(self):
        self.allowed_tables = allowed_tables
        self.ddb_client = boto3.client('dynamodb')

    def __del__(self):
        pass

    def main(self, table, operation):
        if table not in self.allowed_tables:
            print(f"Error: Invalid table name '{table}'.")
            return

        # Generate class name from table name as PasscalCase
        class_name = ''.join(word.capitalize() for word in table.split('_'))
        # Get class object from class name using globals()
        model_class = globals()[class_name]

        if operation == 'scan':
            items = model_class.scan()
            pprint(items)

        elif operation == 'truncate':
            model_class.truncate()
            print(f'{class_name}.delete() executed.')

        elif operation == 'delete':
            model_class.delete_table()
            print(f'{class_name}.delete_table() executed.')

        elif operation == 'desc':
            table_name = model_class.get_table_name()
            table_info = self.ddb_client.describe_table(TableName=table_name)
            pprint((table_info))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('table', choices=allowed_tables,
                        help="Choose the table: 'field' or 'post'")
    parser.add_argument('operation', choices=[
                        'scan', 'delete', 'truncate', 'desc'], help='Choose the operation')
    args = parser.parse_args()

    scanner = TableUtilHandler()
    scanner.main(args.table, args.operation)
