#!/usr/bin/env python
import smtplib
import os
import pandas as pd
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

me = "student.polesmielgo@galvanize.it"
you = "carles.poles@gmail.com"

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "MeetUp Reports Timestamp"
msg['From'] = me
msg['To'] = you


def file_time(file_name):

    try:
        mtime = os.path.getmtime(file_name)
    except OSError:
        mtime = 0
    last_modified_date = datetime.fromtimestamp(mtime)

    return last_modified_date


if __name__ == "__main__":
    file_list = ['spark-meetings-map.html', 'spark-top-meetup-categories.html',
                 'spark-top-meetup-categories-pie.html',
                 'spark-top-meetup-organizers.html',
                 'spark-top-meetup-organizers-pie.html',
                 'spark-top-meetup-topics.html',
                 'spark-top-meetup-topics-pie.html']

    time_list = []

    for f in file_list:
        time_list.append(file_time(f))

    final_list = zip(file_list, time_list)

    file_df = pd.DataFrame(final_list,
                           columns=['file_name', 'timestamp'])

    file_df.index = file_df.index + 1

    html_page = '<!DOCTYPE html><HTML><HEAD>\
    <TITLE>Timestamp of MeetUp Reports</TITLE></HEAD>\
    <BODY>{}</BODY></HTML>'.format(file_df.to_html())

    with open("meetup_report_files.html", "w") as f:
        f.write("<h1>Timestamp of MeetUp Reports</h1>")
        f.write(html_page)

    # Create the body of the message (a plain-text and an HTML version).
    text = "Here is the link to the report:\n\nhttps://s3-us-west-1.amazonaws.com/dsci6007.com/meetup_report_files.html"

    html = """\
    <html>
      <head></head>
      <body>
        <h1>MeetUp Reports</h1>
        <h2>Timestamp of Report Generation.</h2>
        <p>You can also view the report here:<br>
        <a href="https://s3-us-west-1.amazonaws.com/dsci6007.com/meetup_report_files.html">link</a>.
        """ + file_df.to_html() + """</p>
        <p>Landing page to view&nbsp;
        <a href="https://s3-us-west-1.amazonaws.com/dsci6007.com/meetup_summary_reports.html">each report</a>.</p>
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
