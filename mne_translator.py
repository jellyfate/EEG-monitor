from brainflow.board_shim import BoardShim
from mne import create_info
from mne.io import RawArray
from mne.time_frequency import psd_array_multitaper
from numpy import asarray, logical_and, argmax, where
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

    def flatten_data(self, data):
        flattened_data = {}
        for channel_data in data:
            for channel_name, inner_data in channel_data.items():
                flattened_data[channel_name] = inner_data[1]
        return flattened_data

    def get_bandpower(self, data, bands):
        # use spectral analysis method by filtering the original signal
        # with a set of optimal bandpass filter, called Slepian sequences
        psd, freqs = psd_array_multitaper(
            x=asarray(data),
            sfreq=self.sfreq/2,
            fmin=0, fmax=47,
            adaptive=True,
            normalization='full',
            n_jobs=4,
            verbose=False
        )
        # frequency resolution
        freq_res = freqs[1] - freqs[0]
        # total integral approximation of the spectrum using parabola (Simpson's rule)
        total_bp = simps(psd, dx=freq_res)

        powers, main_freqs = {}, {}
        for band_name, band in bands.items():
            low, high = asarray(band)
            # find index of band in frequency vector
            band_index = logical_and(freqs >= low, freqs <= high)
            # one band integral approximation of the spectrum using parabola (Simpson's rule)
            bp = simps(psd[band_index], dx=freq_res)
            powers[band_name] = bp / total_bp
            freq_index = band_index.tolist().index(True) + argmax(psd[band_index])
            main_freqs[band_name] = freqs[freq_index]
        return powers, main_freqs
