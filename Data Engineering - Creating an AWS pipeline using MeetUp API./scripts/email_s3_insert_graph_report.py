#!/usr/bin/env python
import smtplib
import boto
import ssl
import sys
import os
import yaml
import psycopg2
import StringIO
import urllib
import base64
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from boto.s3.connection import S3Connection
from boto.s3.key import Key
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

rds_credentials = yaml.load(open(os.path.expanduser('~/aws_rds_cred.yml')))

DB_NAME = rds_credentials['s3_final_project_postgres']['dbname']
DB_USER = rds_credentials['s3_final_project_postgres']['user']
DB_HOST = rds_credentials['s3_final_project_postgres']['host']
DB_PASSWORD = rds_credentials['s3_final_project_postgres']['password']

try:
    conn = psycopg2.connect("dbname='" + DB_NAME + "' user='" + DB_USER +
                            "' host='" + DB_HOST + "' password='" +
                            DB_PASSWORD + "'")
except:
    print "Unable to connect to the database in RDS."

if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

conn_s3 = S3Connection(host='s3.amazonaws.com')

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

    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO s3_bucket (bucket_name, size, timestamp_firehose, total_objects)\
        VALUES('{}', {}, '{}', {}) ON CONFLICT DO NOTHING".format(bucket_name, total_gigs, datetime.now(), n))
        conn.commit()
    except:
        print "Unable to execute and commit insert statement."

    try:
        cur.execute("SELECT timestamp_firehose, size\
                FROM s3_bucket WHERE bucket_name = %(bucket_name)s",
                    {'bucket_name': bucket_name})
    except:
        print "Unable to execute select statement."

    size_df = pd.DataFrame(cur.fetchall(), columns=['timestamp', 'size'])

    plot = size_df.plot()
    fig = plot.get_figure()
    fig.savefig("s3_size_plot.png")

    try:
        cur.execute("SELECT timestamp_firehose, total_objects\
                FROM s3_bucket WHERE bucket_name = %(bucket_name)s",
                    {'bucket_name': bucket_name})
    except:
        print "Unable to execute select statement."

    objects_df = pd.DataFrame(cur.fetchall(), columns=['timestamp',
                                                       'total_objects'])

    plot = objects_df.plot()
    fig = plot.get_figure()
    fig.savefig("s3_objects_plot.png")

    website_bucket = conn_s3.get_bucket('dsci6007.com')

    k = Key(website_bucket)
    k.key = 'images/s3_size_plot.png'
    k.set_contents_from_filename("s3_size_plot.png")

    k.key = 'images/s3_objects_plot.png'
    k.set_contents_from_filename("s3_objects_plot.png")

    timestamp = '{}'.format(datetime.now())

    html_report = '<html lang="en">\
      <head>\
      <meta charset="utf-8">\
      <title>S3 Firehose Bucket Report</title>\
      </head>\
      <body>\
      <h2>S3 bucket size over time:</h2>\
      <img src="images/s3_size_plot.png" />\
      <br/>\
      <h2>S3 bucket number of objects over time:</h2>\
      <img src="images/s3_objects_plot.png" /></body>\
      </html>'

    with open("s3_report.html", "w") as outf:
            outf.write("<h1>As of: " + timestamp + "</h1>")
            outf.write(html_report)

    k.key = 's3_report.html'
    k.set_contents_from_filename("s3_report.html")

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
        <p><b>Plot of GB over time:</b><br/> <img src='https://s3-us-west-1.amazonaws.com/dsci6007.com/images/s3_size_plot.png'/></p>
        <p><b>Plot of objects over time:</b><br/> <img src='https://s3-us-west-1.amazonaws.com/dsci6007.com/images/s3_objects_plot.png'/></p>
      </body>
    </html>
    """

    cur.close()
    conn.close()

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
    # sendmail function takes 3 arguments: sender's address,
    # recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(me, you, msg.as_string())
    s.quit()
