#!/usr/bin/env python
import smtplib
import boto
import ssl
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

me = "student.polesmielgo@galvanize.it"
you = "carles.poles@gmail.com"

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "S3 Firehose Size Report"
msg['From'] = me
msg['To'] = you

s3 = boto.connect_s3(host='s3.amazonaws.com')

if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

# https://gist.github.com/robinkraft/2667939

# based on http://www.quora.com/Amazon-S3/What-is-the-fastest-way-to-measure-the-total-size-of-an-S3-bucket


def get_bucket_size(bucket_name):
    bucket = s3.lookup(bucket_name)
    total_bytes = 0
    n = 0
    for key in bucket:
        total_bytes += key.size
        n += 1
        if n % 2000 == 0:
            print(n)
    total_gigs = total_bytes/1024/1024/1024
    print("%s: %i GB, %i objects" % (bucket_name, total_gigs, n))
    return total_gigs, n


bucket_list = []
bucket_sizes = []

for bucket_name in bucket_list:
    size, object_count = get_bucket_size(bucket_name)
    bucket_sizes.append(dict(name=bucket_name, size=size, count=object_count))


print("\nTotals:")
for bucket_size in bucket_sizes:
    print("%s: %iGB, %i objects" % (bucket_size["name"], bucket_size["size"],
                                    bucket_size["count"]))


if __name__ == "__main__":
    bucket_name = sys.argv[1]
    # Execute Main functionality
    total_gigs, n = get_bucket_size(bucket_name)

    # Create the body of the message (a plain-text and an HTML version).
    text = "S3 Bucket Size Report\n" + \
        "MeetUp Firehose\n\n" + \
        "Timestamp:" + '{}'.format(datetime.now()) + "\n" + \
        "Bucket Name:" + str(bucket_name) + "\n" + \
        "Number of Objects:" + str(n) + "\n"

    html = """\
    <html>
      <head></head>
      <body>
        <h1>S3 Bucket Size Report</h1>
        <h2>MeetUp Firehose</h2>
        <p><b>Timestamp:</b> """ + '{}'.format(datetime.now()) + """</p>
        <p><b>Bucket Name:</b> """ + str(bucket_name) + """</p>
        <p><b>Bucket Size:</b> """ + str(total_gigs) + """ GB</p>
        <p><b>Number of Objects:</b> """ + str(n) + """</p>
      </body>
    </html>
    """

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    s = smtplib.SMTP('localhost')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(me, you, msg.as_string())
    s.quit()
    # Usage example: $python email_s3_report.py dsci6007-firehose-final-project
