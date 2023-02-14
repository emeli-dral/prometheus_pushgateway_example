import datetime
import random
import time
import logging
import pandas as pd
import requests
import zipfile
import io

from evidently import ColumnMapping
from evidently.report import Report
from evidently.metrics import DatasetMissingValuesMetric, DatasetDriftMetric, DatasetSummaryMetric

from prometheus_client import CollectorRegistry, push_to_gateway, Gauge, Counter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10
registry = CollectorRegistry()

# data loading
content = requests.get("https://archive.ics.uci.edu/ml/machine-learning-databases/00275/Bike-Sharing-Dataset.zip").content
with zipfile.ZipFile(io.BytesIO(content)) as arc:
    raw_data = pd.read_csv(arc.open("day.csv"), header=0, sep=',', parse_dates=['dteday'], index_col='dteday')

# create metrics
#simple_counter = Counter('simple_counter', 'Example Counter metric', registry=registry)
#simple_gauge = Gauge('simple_gauge', 'Example Simple Gauge metric', registry=registry)
#second_gauge = Gauge('second_gauge', 'Example Second Simple Gauge metric', registry=registry)
#second_gauge.set(10)
#rand = random.Random()

#def calculate_metrics():
#    value = rand.random()
#    simple_gauge.set(value)
#    simple_counter.inc()
#    simple_hist.observe(value)

# create metrics
simple_counter = Counter('simple_counter', 'Number of Observation', registry=registry)
drift_gauge = Gauge('drift_gauge', 'Number of Drifted Columns', registry=registry)
missing_gauge = Gauge('missing_gauge', 'Number of Missing Values', registry=registry)
almost_duplicated_gauge = Gauge('almost_duplicated_gauge', 'Number of Almost Duplicated Columns', registry=registry)

# create metrics
reference_data = raw_data.loc['2011-01-01 00:00:00':'2011-01-28 23:00:00']
begin = datetime.datetime(2011,1,20,0,0)
end = datetime.datetime(2011,1,20,23,59)

report = Report(metrics=[
    DatasetMissingValuesMetric(), 
    DatasetDriftMetric(), 
    DatasetSummaryMetric()
])

def calculate_evidently_metrics(i):
    current_data = raw_data[begin + datetime.timedelta(i) : end + datetime.timedelta(i)]
    report.run(reference_data=reference_data, current_data=current_data)
    result = report.as_dict()

    drift = result['metrics'][1]['result']['number_of_drifted_columns']
    duplicated_cols = result['metrics'][2]['result']['current']['number_of_almost_duplicated_columns']
    missing_values = result['metrics'][0]['result']['number_of_missing_values']

    simple_counter.inc(current_data.shape[0])
    drift_gauge.set(drift)
    missing_gauge.set(duplicated_cols)
    almost_duplicated_gauge.set(missing_values)

def main():
    last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)
    for i in range(0, 100):
        #calculate_metrics()
        calculate_evidently_metrics(i)
        # this sends all metrics to gateway so prometheus can scrape it
        new_send = datetime.datetime.now()
        seconds_elapsed = (new_send - last_send).total_seconds()
        if seconds_elapsed < SEND_TIMEOUT:
            time.sleep(SEND_TIMEOUT - seconds_elapsed)
        push_to_gateway('localhost:9091', job='batchA', registry=registry)
        while last_send < new_send:
            last_send = last_send + datetime.timedelta(seconds=10)
        logging.info("data sent")


if __name__ == '__main__':
    main()
