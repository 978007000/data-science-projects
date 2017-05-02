
import sys
import boto3
from boto.s3.connection import S3Connection
from pyspark.sql.functions import explode
from pyspark.sql.functions import col
from datetime import datetime
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession

# Constants
APP_NAME = "MeetUp Topics"

conn = S3Connection(host='s3.amazonaws.com')

client = boto3.client('s3', region_name='us-east-1',
                      endpoint_url='http://s3.amazonaws.com')

bucket = conn.get_bucket('dsci6007-final-project-3nf')


def main(sc, filename):
    """"
    INPUT: S3 bucket with raw json files.
    We will apply a series of spark dataframe transformations to the files.
    OUTPUT: save the results in 3NF as csv files in S3 and
    several reports in html format in the master node.
    """
    try:
        df = spark.read.json(filename)

        timestamp = '{}'.format(datetime.now())

        timestamp_file = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        results_df_1 = df.select('results')

        results_df_2 = results_df_1.select(results_df_1['results'])

        results_df_2_1 = results_df_2.select(explode(
            results_df_2['results']['category'])).distinct()

        results_df_2_1_no_unique = results_df_2.select(
            explode(results_df_2['results']['category']))

        category_df = results_df_2_1.select(
            results_df_2_1.col['id'].alias('category_id'),
            results_df_2_1.col['shortname'].alias('category_shortname'),
            results_df_2_1.col['name'].alias('category_name')).where(
            results_df_2_1.col['id'].isNotNull())

        category_no_unique_df = results_df_2_1_no_unique.select(
            results_df_2_1_no_unique.col['id'].alias('category_id'),
            results_df_2_1_no_unique.col['shortname']
            .alias('category_shortname'),
            results_df_2_1_no_unique.col['name'].alias('category_name'))\
            .where(results_df_2_1_no_unique.col['id'].isNotNull())

        # response_c = client.put_object(
        #         Bucket='dsci6007-final-project-3nf',
        #         Body='',
        #         Key=timestamp_file + '_category_table.csv/'
        #         )

        category_df.write.save('s3a://dsci6007-final-project-3nf/category_table/' + str(timestamp_file) + '_category_table.csv/', format="csv")

        category_count_df = category_no_unique_df\
            .groupBy('category_shortname').count().sort(col("count").desc())

        df_categories = category_count_df.limit(20).toPandas()

        df_categories.index = df_categories.index + 1

        top_list_categories = df_categories.values.tolist()

        top_list_categories_u = [[str(item[0]), item[1]] for item in
                                 top_list_categories]

        top_list_categories_u.insert(0, ['Category', 'Count'])

        top_list_categories_u = top_list_categories_u[:11]

        html_1 = '<!DOCTYPE html><HTML><HEAD><TITLE>Top 20 MeetUp Categories\
                 </TITLE></HEAD><BODY>{}</BODY></HTML>'.format(
                 df_categories.to_html().encode('utf-8'))

        with open("spark-top-meetup-categories.html", "w") as outf:
            outf.write("<H1>Top 20 MeetUp Categories from Spark</H1>")
            outf.write("<H2>As of: " + timestamp + "</H2>")
            outf.write(html_1)

        html_2 = '<html><head><title>Top 10 MeetUp Categories</title>\
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>\
        <script type="text/javascript">       google.charts.load(\'current\',\
        {\'packages\':[\'corechart\']});\
        google.charts.setOnLoadCallback(drawChart);\
        function drawChart() { var data = google.visualization.arrayToDataTable(%s);\
        var options = {           title: \'Top 10 Categories Breakdown\'};\
        var chart = new google.visualization.PieChart(document.getElementById(\'piechart\'));\
        chart.draw(data, options);       }     </script></head><body>\
        <h1>Top 10 MeetUp Categories from Spark</h1>\
        <div id="piechart" style="width: 900px; height: 500px;"></div> </body>\
        </html>'%(top_list_categories_u)

        with open("spark-top-meetup-categories-pie.html", "w") as outf:
            outf.write("<H2>As of: " + timestamp + "</H2>")
            outf.write(html_2)

        results_df_2_2 = results_df_2.select(explode(results_df_2['results']
                                                     ['topics'])).distinct()

        results_df_2_2_no_unique = results_df_2.select(explode(
            results_df_2['results']['topics']))

        results_df_2_2_1 = results_df_2_2.select(explode(results_df_2_2.col))

        results_df_2_2_1_no_unique = results_df_2_2_no_unique.select(
            explode(results_df_2_2_no_unique.col))

        topic_df = results_df_2_2_1.select(
            results_df_2_2_1.col['id'].alias('topic_id'),
            results_df_2_2_1.col['name'].alias('topic_name'),
            results_df_2_2_1.col['urlkey'].alias('topic_urlkey')).where(
            results_df_2_2_1.col['id'].isNotNull())

        topic_no_unique_df = results_df_2_2_1_no_unique.select(
            results_df_2_2_1_no_unique.col['id'].alias('topic_id'),
            results_df_2_2_1_no_unique.col['name'].alias('topic_name'),
            results_df_2_2_1_no_unique.col['urlkey'].alias('topic_urlkey'))\
            .where(results_df_2_2_1_no_unique.col['id'].isNotNull())

        # response_t = client.put_object(
        #         Bucket='dsci6007-final-project-3nf',
        #         Body='',
        #         Key=timestamp_file + '_topic_table.csv/'
        #         )

        topic_df.write.save('s3a://dsci6007-final-project-3nf/topic_table/' + str(timestamp_file) + '_topic_table.csv/', format="csv")
        # topic_df.write.save('s3a://dsci6007-final-project-3nf/topic_table/topic_table.csv/', format="csv")

        topic_count_df = topic_no_unique_df.groupBy('topic_name')\
            .count().sort(col("count").desc())

        df_topic = topic_count_df.limit(20).toPandas()

        df_topic.index = df_topic.index + 1

        top_list_topics = df_topic.values.tolist()

        top_list_topics_u = [[str(item[0]), item[1]] for item in
                             top_list_topics]

        top_list_topics_u.insert(0, ['Topic', 'Count'])

        top_list_topics_u = top_list_topics_u[:11]

        html_1 = '<!DOCTYPE html><HTML><HEAD><TITLE>Top 20 MeetUp Topics</TITLE>\
        </HEAD><BODY>{}</BODY></HTML>'.format(
            df_topic.to_html().encode('utf-8'))

        with open("spark-top-meetup-topics.html", "w") as outf:
            outf.write("<H1>Top 20 MeetUp Topics from Spark</H1>")
            outf.write("<H2>As of: " + timestamp + "</H2>")
            outf.write(html_1)

        html_2 = '<html><head><title>Top 10 MeetUp Topics</title>\
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>\
        <script type="text/javascript">\
        google.charts.load(\'current\',\
        {\'packages\':[\'corechart\']});\
        google.charts.setOnLoadCallback(drawChart);\
        function drawChart() { var data = google.visualization.arrayToDataTable(%s);\
        var options = {title: \'Top 10 Topics Breakdown\'};\
        var chart = new google.visualization.PieChart(document.getElementById(\'piechart\'));\
        chart.draw(data, options);       }     </script></head><body>\
        <h1>Top 10 MeetUp Topics from Spark</h1>\
        <div id="piechart" style="width: 900px; height: 500px;"></div>\
        </body> </html>'%(top_list_topics_u)

        with open("spark-top-meetup-topics-pie.html", "w") as outf:
            outf.write("<H2>As of: " + timestamp + "</H2>")
            outf.write(html_2)

        results_df_2_3_no_unique = results_df_2.select(explode(
            results_df_2['results']['organizer']))

        results_df_2_3 = results_df_2_3_no_unique.distinct()

        organizer_df = results_df_2_3.select(
            results_df_2_3.col['member_id'].alias('member_id'),
            results_df_2_3.col['name'].alias('organizer_name')).where(
            results_df_2_3.col['member_id'].isNotNull())

        organizer_no_unique_df = results_df_2_3_no_unique.select(
            results_df_2_3_no_unique.col['member_id'].alias('member_id'),
            results_df_2_3_no_unique.col['name'].alias('organizer_name'))\
            .where(results_df_2_3_no_unique.col['member_id'].isNotNull())

        # response_o = client.put_object(
        #         Bucket='dsci6007-final-project-3nf',
        #         Body='',
        #         Key=timestamp_file + '_organizer_table.csv/'
        #         )

        organizer_df.write.save('s3a://dsci6007-final-project-3nf/organizer_table/' + str(timestamp_file) + '_organizer_table.csv/', format="csv")
        # organizer_df.write.save('s3a://dsci6007-final-project-3nf/organizer_table/organizer_table.csv/', format="csv")

        organizer_count_df = organizer_no_unique_df.groupBy('organizer_name')\
            .count().sort(col("count").desc())

        df_organizer = organizer_count_df.limit(20).toPandas()

        df_organizer.index = df_organizer.index + 1

        top_list_organizer = df_organizer.values.tolist()

        top_list_organizer_u = [[str(item[0]), item[1]] for item in
                                top_list_organizer]

        top_list_organizer_u.insert(0, ['Organizer', 'Count'])

        top_list_organizer_u = top_list_organizer_u[:11]

        html_1 = '<!DOCTYPE html><HTML><HEAD><TITLE>Top 20 MeetUp Organizers</TITLE>\
        </HEAD><BODY>{}</BODY></HTML>'\
        .format(df_organizer.to_html().encode('utf-8'))

        with open("spark-top-meetup-organizers.html", "w") as outf:
            outf.write("<H1>Top 20 MeetUp Organizers from Spark</H1>")
            outf.write("<H2>As of: " + timestamp + "</H2>")
            outf.write(html_1)

        html_2 = '<html><head><title>Top 10 MeetUp Organizers</title>\
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>\
        <script type="text/javascript">\
        google.charts.load(\'current\', {\'packages\':[\'corechart\']});\
        google.charts.setOnLoadCallback(drawChart);\
        function drawChart() { var data = google.visualization.arrayToDataTable(%s);\
        var options = {           title: \'Top 10 Organizers Breakdown\'};\
        var chart = new google.visualization.PieChart(document.getElementById(\'piechart\'));\
        chart.draw(data, options);       }     </script></head><body>\
        <h1>Top 10 MeetUp Organizers from Spark</h1>\
        <div id="piechart" style="width: 900px; height: 500px;"></div> </body>\
        </html>'%(top_list_organizer_u)

        with open("spark-top-meetup-organizers-pie.html", "w") as outf:
            outf.write("<H2>As of: " + timestamp + "</H2>")
            outf.write(html_2)

    except Exception as e:
        print("Error: ", str(e))


if __name__ == "__main__":
    # Configure Spark
    conf = SparkConf().setAppName(APP_NAME)
    conf = conf.setMaster("local[*]")
    sc = SparkContext(conf=conf)
    sc.setLogLevel("WARN")
    spark = SparkSession.builder \
        .master("local") \
        .appName("MeetUp") \
        .config("spark.some.config.option", "some-value") \
        .getOrCreate()

    filename = sys.argv[1]
    # Execute Main functionality
    main(sc, filename)
