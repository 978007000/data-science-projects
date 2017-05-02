import ssl
import sys
from boto.s3.connection import S3Connection

# http://stackabuse.com/example-upload-a-file-to-aws-s3/


def upload_to_s3(file, bucket):
    """
    Uploads the given file to the AWS S3
    bucket.
    """

    conn = S3Connection(host='s3.amazonaws.com')

    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    website_bucket = conn.get_bucket(bucket)

    output_file = website_bucket.new_key(file)
    output_file.content_type = 'text/html'
    output_file.set_contents_from_filename(file, policy='public-read')


if __name__ == '__main__':
    try:
        file = sys.argv[1]
        upload_to_s3(file, 'dsci6007.com')
    except Exception as e:
        print("Error:", str(e))

# example usage: $python send_file_s3_bucket.py my_file.html
