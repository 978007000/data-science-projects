
from boto.s3.connection import S3Connection
from datetime import datetime
import boto3

conn = S3Connection(host='s3.amazonaws.com')

timestamp_file = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

client = boto3.client('s3', region_name='us-east-1', endpoint_url='http://s3.amazonaws.com')

response = client.put_object(
        Bucket='dsci6007-final-project-3nf',
        Body='',
        Key=timestamp_file + '_category_table/'
        )

bucket = conn.get_bucket('dsci6007-final-project-3nf')
print(bucket.get_key(timestamp_file + '_category_table/'))
