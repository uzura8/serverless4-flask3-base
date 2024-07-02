""" Copy items from one DynamoDB table to another DynamoDB table """

import os
import sys
import argparse
import boto3


parent_dir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

# # Table name for copy from
# source_table_name = 'table-name-copied-from'
#
# # Table name for copy to
# destination_table_name = 'table-name-copied-to'

class CopyTableItemsHandler:
    """ Copy items from one DynamoDB table to another DynamoDB table """
    def __init__(self):
        # self.allowed_tables = allowed_tables
        # self.ddb_client = boto3.client('dynamodb')

        # Create boto3 DynamoDB client
        self.dynamodb = boto3.resource('dynamodb')

    def __del__(self):
        pass

    def main(self, from_table, to_table):
        """ Main function """
        # Get table copied from
        source_table = self.dynamodb.Table(from_table)

        # Get table copied to
        destination_table = self.dynamodb.Table(to_table)

        # ExclusiveStartKey to set start position for scan
        exclusive_start_key = None

        while True:
            # Get items from table copied from to set start position
            scan_kwargs = {}
            if exclusive_start_key:
                scan_kwargs['ExclusiveStartKey'] = exclusive_start_key

            response = source_table.scan(**scan_kwargs)

            # Insert items to table copied to
            with destination_table.batch_writer() as batch:
                for item in response['Items']:
                    batch.put_item(Item=item)

            # Break loop on not exits ExclusiveStartKey
            if 'LastEvaluatedKey' not in response:
                break

            # Set start potions for next scan
            exclusive_start_key = response['LastEvaluatedKey']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('from_table', help="Choose the copy from table")
    parser.add_argument('to_table', help="Choose the copy totable")
    args = parser.parse_args()

    handler = CopyTableItemsHandler()
    handler.main(args.from_table, args.to_table)
