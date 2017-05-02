#!/usr/bin/env python
import os
import yaml
import ssl
import psycopg2
import psycopg2.extras
import re
from boto.s3.connection import S3Connection

rds_credentials = yaml.load(open(os.path.expanduser('~/aws_rds_cred.yml')))

conn = S3Connection()


def main(rds_credentials, conn):

    DB_NAME = rds_credentials['final_project_postgres']['dbname']
    DB_USER = rds_credentials['final_project_postgres']['user']
    DB_HOST = rds_credentials['final_project_postgres']['host']
    DB_PASSWORD = rds_credentials['final_project_postgres']['password']

    data_bucket = conn.get_bucket('dsci6007-final-project-3nf')

    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

        try:
            conn = psycopg2.connect("dbname='" + DB_NAME + "' user='" +
                                    DB_USER +
                                    "' host='" + DB_HOST +
                                    "' password='" + DB_PASSWORD + "'")
        except:
            print("Unable to connect to the database in RDS.")

    cur = conn.cursor()

    try:
        i = 0
        for key in data_bucket.list():
            # meeting
            if re.match(r"meeting_table/meeting_table", key.name):
                if re.findall(r"part-", key.name) and key.size > 0:
                    data_key = data_bucket.get_key(key)
                    data = data_key.get_contents_as_string()
                    data = data.split("\n")
                    for items in data:
                        elements = items.split(",")
                        try:
                            if elements[0]:
                                elements[0] = re.sub('[()]', '', elements[0])
                                id = int(elements[0])

                                cat_id = int(elements[1])
                                elements[2] = re.sub("u'", '', elements[2])
                                elements[2] = re.sub("'", '', elements[2])
                                city = str(elements[2]).strip()
                                lon = round(float(elements[3]), 4)
                                lat = round(float(elements[4]), 4)
                                mem = int(elements[5])
                                elements[6] = re.sub("u'", '', elements[6])
                                elements[6] = re.sub("'", '', elements[6])
                                url = str(elements[6]).strip()
                                elements[7] = re.sub("u'", '', elements[7])
                                elements[7] = re.sub("'", '', elements[7])
                                name = str(elements[7]).strip()
                                elements[8] = re.sub("u'", '', elements[8])
                                elements[8] = re.sub("'", '', elements[8])
                                desc = str(elements[8]).strip()
                                # We use [-1] to make sure we capture the last element of the list,
                                # as we split on "," and unfortunately, the description field has many ",".
                                elements[-1] = re.sub('[()]', '', elements[-1])
                                memb_id = int(elements[-1])

                                cur.execute("INSERT INTO meeting (meeting_id, category_id, city, longitude, latitude, members, url, name, description, member_id)\
                                    VALUES({}, {}, '{}', {}, {}, {}, '{}', '{}', '{}', {}) ON CONFLICT DO NOTHING".format(id, cat_id, city, lon, lat, mem, url, name, desc, memb_id))

                                i += 1
                                # We commit inserts every 100 items.
                                if i % 100 == 0:
                                    conn.commit()
                        except ValueError:
                            pass
    except:
        print("Unable to execute and commit insert statement.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main(rds_credentials, conn)
