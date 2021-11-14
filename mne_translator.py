from brainflow.board_shim import BoardShim
from mne import create_info
from mne.io import RawArray
from mne.time_frequency import psd_array_multitaper
from numpy import asarray, logical_and
from scipy.integrate import simps
from scipy.signal import welch

from globals import *


class MNETranslator:
    def __init__(self):
        self.eeg_channels = BoardShim.get_eeg_channels(BOARD_ID)
        self.sfreq = BoardShim.get_sampling_rate(BOARD_ID)
        self.ch_types = ['eeg'] * len(self.eeg_channels)
        self.info = create_info(
            ch_names=CHANNELS_NAMES, sfreq=self.sfreq, ch_types=self.ch_types)
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

    def get_bandpower(self, data, bands):
        # use spectral analysis method by filtering the original signal
        # with a set of optimal bandpass filter, called Slepian sequences
        psd, freqs = psd_array_multitaper(asarray(data), self.sfreq, adaptive=True,
                                          normalization='full', verbose=0, n_jobs=4)
        # frequency resolution
        freq_res = 0.25
        # total integral approximation of the spectrum using parabola (Simpson's rule)
        total_bp = simps(psd, dx=freq_res)

        result = {}
        for band_name, band in bands.items():
            low, high = asarray(band)
            # find index of band in frequency vector
            idx_band = logical_and(freqs >= low, freqs <= high)
            # one band integral approximation of the spectrum using parabola (Simpson's rule)
            bp = simps(psd[idx_band], dx=freq_res)
            result[band_name] = bp / total_bp
        return result
