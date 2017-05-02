
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import timedelta
import iso8601

bucket_input = 'dsci6007-firehose-final-project'

default_args = {
  'owner': 'airflow',
  'depends_on_past': False,
  'start_date': iso8601.parse_date("2017-03-07"),
  'email': ['carles.poles@gmail.com'],
  'email_on_failure': True,
  'email_on_retry': True,
  'retries': 3,
  'retry_delay': timedelta(minutes=1),
}

# Timedelta 1 is 'run daily', for example:
# schedule_interval=timedelta(1)
# To run every minute:
# schedule_interval=timedelta(minutes=1)

dag = DAG(
  'meetup_s3_airflow',
  schedule_interval='@hourly',
  default_args=default_args
)

# Run a simple Python Script.
# IMPORTANT!! Even though the python executable script lives
# in /home/ubuntu, we do not specify the bash_command as:
# bash_command='/home/ubuntu email_s3_report.py '
# BUT instead as:
# bash_command='~/./email_s3_report.py '
python_s3_bucket_report = BashOperator(
  task_id='python_s3_bucket_report',
  bash_command='~/./email_s3_report.py '
  + bucket_input,
  dag=dag
)
