
import json
import sys
import pandas as pd
from pyspark import SparkConf, SparkContext

# Constants
APP_NAME = "MeetUp RDD"


def split_file(data):
    return data.split("|||")


def filter_results(data):
    try:
        result = json.loads(data)
        if 'results' in result:
            results = result.get('results')
            return True
        return False
    except:
        return False


def get_results(data):
    try:
        result = json.loads(data)
        if 'results' in result:
            results = result.get('results')
            return results
    except:
        pass


def flat_results(data):
    return data


def filter_category(data):
    try:
        if 'id' in data['category']:
            return True
        return False
    except:
        return False


def get_meeting(data):
    try:
        if 'id' in data:
            if 'member_id' in data['organizer']:
                if 'id' in data['category']:
                    return (data['id'], data['category']['id'], data['city'],
                            data['lon'], data['lat'],
                            data['members'], data['link'], data['name'],
                            data['description'],
                            data['organizer']['member_id'])
    except:
        pass


def get_category(data):
    try:
        if 'id' in data['category']:
            return (data['category']['id'], data['category']['shortname'],
                    data['category']['name'])
    except:
        pass


def filter_organizer(data):
    try:
        if 'member_id' in data['organizer']:
            return True
        return False
    except:
        return False


def get_organizer(data):
    try:
        if 'member_id' in data['organizer']:
            return (data['organizer']['member_id'], data['organizer']['name'])
    except:
        pass


def filter_meeting_topic(data):
    try:
        if 'id' in data:
            topics = data['topics']
        if topics:
            return True
        return False
    except:
        return False


def get_meeting_topic(data):
    try:
        if 'id' in data:
            topics = data['topics']
        if topics:
            return [(data['id'], topic['id']) for topic in topics]
    except:
        pass


def make_tuples(data):
    try:
        return tuple(tuple(x) for x in data)
    except:
        pass


def get_map_info(data):
    try:
        if 'id' in data:
            return round(data['lat'], 4), round(data['lon'], 4), data['city']
    except:
        pass


def main(sc, filename):
    """"
    INPUT: S3 bucket with text files.
    We will apply a series of spark transformations to the files.
    OUTPUT: save the results as text file in S3 and a html file
    in the master node.
    """
    try:
        raw_json = sc.textFile(filename)
        flat_json = raw_json.flatMap(split_file)

        filter_results_i = flat_json.filter(filter_results)

        results_data = filter_results_i.map(get_results)

        results_flat = results_data.flatMap(flat_results)

        meeting_data = results_flat.map(get_meeting)

        meeting_data.saveAsTextFile("s3a://dsci6007-final-project-3nf/meeting_table/meeting_table")

        organizer_filter = results_flat.filter(filter_organizer)

        organizer_data = organizer_filter.map(get_organizer).distinct()

        organizer_data.saveAsTextFile("s3a://dsci6007-final-project-3nf/organizer_table/organizer_table")

        category_filter = results_flat.filter(filter_category)

        category_data = category_filter.map(get_category).distinct()

        category_data.saveAsTextFile("s3a://dsci6007-final-project-3nf/category_table/category_table")

        meeting_topic_filter = results_flat.filter(filter_meeting_topic)

        meeting_topic_data = meeting_topic_filter.map(get_meeting_topic)

        meeting_topic_data.saveAsTextFile("s3a://dsci6007-final-project-3nf/meeting_topic_table/meeting_topic_table")

        meeting_topic_tuple_data = meeting_topic_data.map(make_tuples)

        meeting_topic_tuple_data.saveAsTextFile("s3a://dsci6007-final-project-3nf/meeting_topic_tuple_table/meeting_topic_tuple_table")

        map_data = results_flat.map(get_map_info).distinct()

        map_df = pd.DataFrame(map_data.take(50),
                              columns=['latitude', 'longitude', 'city'])

        map_list = map_df.values.tolist()

        map_list_u = [[item[0], item[1], str(item[2])] for item in map_list]

        map_list_u.insert(0, ['Latitude', 'Longitude', 'City'])

        html = '<html><head><title>MeetUp Meetings Google Map</title>\
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>\
        <script type="text/javascript">\
        google.charts.load("upcoming", {mapsApiKey:"AIzaSyDjGP2WO7f5lJgHMVde3g_JPjVvekeod34", packages:["map","corechart"]});\
        google.charts.setOnLoadCallback(drawChart);\
        function drawChart() {  var data = google.visualization.arrayToDataTable(%s);\
        var map = new google.visualization.Map(document.getElementById(\'map_div\'));\
        map.draw(data, {  showTooltip: true, showInfoWindow: true });\
        }</script></head><body><h1>MeetUp Meetings Google Map from Spark</h1>\
        <div id="map_div" style="width: 400px; height: 300px"></div></body></html>'%(map_list_u)

        with open("spark-meetings-map.html", "w") as outf:
                    outf.write(html)
    except Exception as e:
        print("Error: ", str(e))


if __name__ == "__main__":
    # Configure Spark
    conf = SparkConf().setAppName(APP_NAME)
    conf = conf.setMaster("local[*]")
    sc = SparkContext(conf=conf)
    filename = sys.argv[1]
    # Execute Main functionality
    main(sc, filename)
