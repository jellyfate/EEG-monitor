from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from globals import *


class Database:
    def __init__(self):
        client = InfluxDBClient(
            url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        self.write_api = client.write_api(write_options=SYNCHRONOUS)
        self.query_api = client.query_api()

    def write(self, data):
        self.write_api.write(
            bucket=INFLUX_BUCKET,
            record=data,
            data_frame_measurement_name='cpu',
            data_frame_tag_columns=['cpu']
        )
