import logging
from time import time

from redis.exceptions import ResponseError
from redistimeseries.client import Client as RedisClient

from globals import *
from mne_translator import MNETranslator


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
        self.mne_translator = MNETranslator()

    def _create_timeseries_storage(self, name):
        try:
            self.connection.info(channel)
        except ResponseError as e:
            self.connection.create(channel, labels={'eeg': 'microvolts'})

    def connect(self):
        self.connection = RedisClient(
            host=self.host,
            port=self.port,
            password=self.password
        )
        for channel in self.channels_names:
            self._create_timeseries_storage(channel)

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

    def pull_eeg(self, start, end, to_raw_array=False):
        stored_eeg = self.connection.mrange(start, end, ('eeg=microvolts',))
        if not to_raw_array:
            return stored_eeg
        raw_array = self.mne_translator.translate_to_raw_array(stored_eeg)
        return raw_array

    def store_processing_result(self, key, timestamp, value):
        self.connection.add(key, timestamp, value)
