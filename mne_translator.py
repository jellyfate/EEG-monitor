from brainflow.board_shim import BoardShim
from mne import create_info
from mne.io import RawArray

from globals import *


class MNETranslator:
    def __init__(self):
        self.eeg_channels = BoardShim.get_eeg_channels(BOARD_ID)
        sfreq = BoardShim.get_sampling_rate(BOARD_ID)
        ch_types = ['eeg'] * len(self.eeg_channels)
        self.info = create_info(
            ch_names=CHANNELS_NAMES, sfreq=sfreq, ch_types=ch_types)

    def _transform_data(self, data):
        # BrainFlow returns uV, convert to V for MNE
        return data[self.eeg_channels, :] / 1000000

    def raw(self, data):
        # convert data to MNE Raw Array
        return RawArray(self._transform_data(data), self.info)
