import logging
import boto3
from botocore.exceptions import ClientError

ACCESS_KEY= 'AKIA4V6OHEKKXRIPMOOS'
SECRET_KEY = '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'


class Amazon_connection:
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY
        )

    def get_object(self, bucket_name, object_name):
        try:
            response = self.client.get_object(Bucket=bucket_name, Key=object_name, ResponseContentEncoding='UTF8')
        except ClientError as e:
            logging.error(e)
            return None
        return response['Body'].read().decode('utf-8')
