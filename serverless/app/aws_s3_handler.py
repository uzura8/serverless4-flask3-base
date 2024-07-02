"""AWS S3 Handler class to handle AWS S3 operations."""

import json
import boto3
from botocore.exceptions import (
    BotoCoreError, ClientError, ParamValidationError, NoCredentialsError
)


class AwsS3Handler:
    """AWS S3 Handler class to handle AWS S3 operations."""
    client = None
    # resource = None
    bucket = None

    def __init__(self, bucket):
        self.bucket = bucket
        self.client = boto3.client('s3')

    def __del__(self):
        pass

    def get_data(self, path, data_type='raw'):
        """Get data from S3 bucket."""
        s3_data = self.client.get_object(Bucket=self.bucket, Key=path)
        raw_data = s3_data['Body'].read()
        if data_type == 'raw':
            return raw_data

        str_data = s3_data['Body'].read().decode('utf-8')
        if data_type == 'json':
            dict_data = json.loads(str_data)
            return dict_data

        return str_data

    def get_list_by_dir(self, dir_path):
        """Get list of objects by directory path."""
        res = self.client.list_objects(Bucket=self.bucket, Prefix=dir_path)
        return res.get('Contents', [])

    def upload(self, blob, path, mimetype=None):
        """Upload data to S3 bucket."""
        try:
            res = self.client.put_object(
                Body=blob,
                # Body = file_strage.stream.read(),
                # Body = io.BufferedReader(file_strage).read(),
                Bucket=self.bucket,
                ContentType=mimetype,
                Key=path
            )

        except (BotoCoreError, ClientError, ParamValidationError, NoCredentialsError) as e:
            # Log the exception for debugging purposes
            # current_app.logger.error(f"Failed to upload to S3: {e}")
            print(f"Failed to upload to S3: {e}")

            # Wrap the original exception with your custom exception
            raise AwsS3HandlerError(f"Failed to upload to S3: {e}") from e

        return res

    def delete(self, path):
        """Delete data from S3 bucket."""
        res = self.client.delete_object(
            Bucket=self.bucket,
            Key=path
        )
        return res

    def delete_by_dir(self, dir_path):
        """Delete data from S3 bucket by directory path."""
        objs = self.get_list_by_dir(dir_path)
        if len(objs) == 0:
            return None

        delete_keys = {'Objects': [{'Key': obj['Key']} for obj in objs]}
        res = self.client.delete_objects(
            Bucket=self.bucket, Delete=delete_keys)
        return res


class AwsS3HandlerError(Exception):
    """Exception to handle AWS S3 errors in AwsS3Handler class."""
    pass
