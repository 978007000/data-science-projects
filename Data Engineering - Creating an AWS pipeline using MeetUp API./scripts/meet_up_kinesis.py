#!/usr/bin/env python

import json
import requests
import time
import os
import yaml
import boto3

credentials = yaml.load(open(os.path.expanduser('~/api_meetup_cred.yml')))

# http://trendct.org/2015/04/03/using-python-and-r-to-pull-and-analyze-meetup-com-api-data/
# Getting some cities to pull events.
cities = [("San Francisco", "CA"), ("Los Angeles", "CA"), ("San Jose", "CA"),
          ("Chicago", "IL"), ("Bridgeport", "CT"), ("New Haven", "CT"),
          ("New York", "NY"), ("Miami", "FL"), ("Houston", "TX"),
          ("Seattle", "WA"), ("Portland", "OR"), ("Austin", "TX"),
          ("Hartford", "CT"), ("Stamford", "CT"), ("Waterbury", "CT")]

api_key = credentials['meetup'].get('api_key')


def firehose_meetups(cities):
    """
    COMMENTS
    """
    firehose_client = boto3.client('firehose', region_name="us-east-1")

    counter = 0
    # Since we can be throttled out, we only
    # insert records less than 200 times.
    while counter < 200:
        for (city, state) in cities:

            per_page = 200
            offset = 0
            results_we_got = per_page

            while (results_we_got == per_page):
                params = ({"sign": "true", "country": "US", "city": city,
                          "state": state, "radius": 10, "key": api_key,
                           "text_format": "plain", "page": per_page,
                           "offset": offset})
                time.sleep(1)
                # https://www.meetup.com/meetup_api/
                # Documentation: https://www.meetup.com/meetup_api/docs/2/groups/
                request = requests.get("http://api.meetup.com/2/groups",
                                       params=params)
                data = request.json()
                offset += 1
                results_we_got = data['meta']['count']

                try:
                    # We add a "|||" to each tweet so each record goes to
                    # a new line. Note that some content is in html and
                    # uses "\n".
                    response = firehose_client.put_record(
                                        DeliveryStreamName='dsci6007_firehose_meet_up',
                                        Record={'Data': json.dumps(data) + '|||'})
                    counter += 1
                except Exception:
                    print("Problem pushing to firehose.")

            time.sleep(1)

        print("Done inserting 200 records.")


if __name__ == '__main__':
    firehose_meetups(cities)
