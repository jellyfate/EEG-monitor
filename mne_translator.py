from brainflow.board_shim import BoardShim
from mne import create_info
from mne.io import RawArray
import numpy as np

from globals import *


class MNETranslator:
    def __init__(self):
        self.eeg_channels = BoardShim.get_eeg_channels(BOARD_ID)
        sfreq = BoardShim.get_sampling_rate(BOARD_ID)
        ch_types = ['eeg'] * len(self.eeg_channels)
        self.info = create_info(
            ch_names=CHANNELS_NAMES, sfreq=sfreq, ch_types=ch_types)
        self.channels_names = tuple(
            ch for ch in CHANNELS_MAPPING if ch not in ('Timestamp', None))

    def _flatten_data(self, data):
        flattened_data = {}
        for channel_data in data:
            for channel_name, inner_data in channel_data.items():
                flattened_data[channel_name] = inner_data[1]
        return flattened_data

    def _transform_flattened_data_to_numpy_array(self, data):
        np_array = np.zeros((len(CHANNELS_MAPPING), len(
            data[CHANNELS_MAPPING[0]])), dtype=np.float64)

        timestamps = []
        for first_channel_item in data[self.channels_names[0]]:
            timestamps.append(first_channel_item[0])
        np_array[CHANNELS_MAPPING.index('Timestamp')] = timestamps

        for channel_id, channel_name in enumerate(self.channels_names):
            channel_data = []
            for channel_item in data[channel_name]:
                channel_data.append(channel_item[1])
            np_array[channel_id] = channel_data

        return np_array

    def _convert_data(self, data):
        flattened_data = self._flatten_data(data)
        np_array = self._transform_flattened_data_to_numpy_array(
            flattened_data)
        # BrainFlow returns uV, convert to V for MNE
        return np_array[self.eeg_channels, :] / 1000000

    def translate_to_raw_array(self, data):
        # convert data to MNE Raw Array
        return RawArray(self._convert_data(data), self.info)
