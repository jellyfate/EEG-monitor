import logging
from time import time

from redis.exceptions import ResponseError
from redistimeseries.client import Client as RedisClient

from globals import *


class Database:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB):
        self.host = host
        self.port = port
        self.password = password
        self.db = db

        self.logger = logging.getLogger(__name__)
        self.timestamp_channel = CHANNELS_MAPPING.index('Timestamp')
        self.channels_names = tuple(
            ch for ch in CHANNELS_MAPPING if ch not in ('Timestamp', None))

    def _create_timeseries_storage(self, name, labels):
        try:
            self.connection.info(name)
        except ResponseError as e:
            self.connection.create(name, labels=labels)

    def connect(self):
        self.connection = RedisClient(
            host=self.host,
            port=self.port,
            password=self.password
        )
        for channel in self.channels_names:
            self._create_timeseries_storage(channel, {'eeg': 'microvolts'})
            for band in FREQ_BANDS:
                # self.connection.alter(f'{channel}-{band}', labels={'channel': channel, 'band': band, 'type':'power'})
                self._create_timeseries_storage(
                    f'{channel}-{band}', {'channel': channel, 'band': band, 'type':'power'})
                self._create_timeseries_storage(
                    f'{channel}-{band}-freq', {'channel': channel, 'band': band, 'type':'freq'})

        for band in FREQ_BANDS:
            # self.connection.alter(f'{channel}-{band}', labels={'channel': channel, 'band': band})
            self._create_timeseries_storage(
                band, {'band': band, 'type': 'total_band_fraction'})
            self._create_timeseries_storage(
                f'{band}-freq', {'band': band, 'type': 'mean_band_freq'})

        for condition in CONDITIONS:
            self._create_timeseries_storage(condition, {'type': 'condition'})

    def disconect(self):
        self.connection.redis.close()

    def _transform_data_to_list_of_tuples(self, data):
        timestamps = []
        for t in data[self.timestamp_channel]:
            timestamp = int(t * 1000)
            while timestamp in timestamps:
                timestamp += 1
            timestamps.append(timestamp)

        return [(channel, timestamp, data[channel_index][timestamp_index])
                for timestamp_index, timestamp in enumerate(timestamps)
                for channel_index, channel in enumerate(self.channels_names)]

    def store_eeg(self, data):
        data_as_tupples = self._transform_data_to_list_of_tuples(data)
        self.connection.madd(data_as_tupples)

    def pull_eeg(self, start, end):
        return self.connection.mrange(start, end, ('eeg=microvolts',))

    def store_processing_result(self, key, timestamp, value):
        return self.connection.add(key, timestamp, value)

    def store_multiple_processing_result(self, list_of_tuples):
        return self.connection.madd(list_of_tuples)

    def pull_processing_result(self, filters, start, end):
        return self.connection.mrange(start, end, filters)
