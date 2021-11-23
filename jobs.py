from datetime import timedelta
from statistics import mean

from timeloop import Timeloop

from globals import *
from mne_translator import MNETranslator
from utils import get_boudaries, moving_avg


class JobManager:
    def __init__(self, board, database, mne):
        self.timeloop = Timeloop()
        self.board = board
        self.database = database
        self.mne = mne
        self._add_jobs()

    def start_jobs(self):
        self.timeloop.start(block=True)

    def _add_jobs(self):
        self.timeloop._add_job(
            func=self.store_eeg_data,
            interval=timedelta(seconds=INTERVAL),
            database=self.database,
            board=self.board
        )
        self.timeloop._add_job(
            func=self.define_bands,
            interval=timedelta(seconds=INTERVAL),
            database=self.database,
            mne=self.mne,
            pulling_interval=timedelta(seconds=START_OFFSET),
            pulling_offset=timedelta(seconds=END_OFFSET)
        )
        self.timeloop._add_job(
            func=self.define_stress_level,
            interval=timedelta(seconds=INTERVAL),
            database=self.database,
            mne=self.mne,
            pulling_interval=timedelta(seconds=START_OFFSET),
            pulling_offset=timedelta(seconds=END_OFFSET)
        )

    def store_eeg_data(self, board, database):
        data = board.get_data()
        database.store_eeg(data)

    def define_bands(self, database, mne, pulling_interval, pulling_offset):
        now, pull_start, pull_end = get_boudaries(
            pulling_interval, pulling_offset)
        data = mne.flatten_data(database.pull_eeg(pull_start, pull_end))
        if not all(i for i in data.values()):
            return

        prepeared_data = []
        total_bands_power = {band: [] for band in FREQ_BANDS}
        mean_bands_freq = {band: [] for band in FREQ_BANDS}

        for channel_name, channel_data in data.items():
            if channel_name == 'f1':
                continue
            data = list(map(lambda x: x[1] / 1000, channel_data))
            bands_power, band_main_freqs = mne.get_bandpower(data, FREQ_BANDS)

            for band_name, band_power in bands_power.items():
                total_bands_power[band_name].append(band_power)
                prepeared_data.append(
                    (f'{channel_name}-{band_name}', now, band_power)
                )

            for band_name, band_main_freq in band_main_freqs.items():
                mean_bands_freq[band_name].append(band_main_freq)
                prepeared_data.append(
                    (f'{channel_name}-{band_name}-freq', now, band_main_freq)
                )

        prepeared_data.extend((band, now, mean(power))
                              for band, power in total_bands_power.items())
        prepeared_data.extend((f'{band}-freq', now, mean(freqs))
                              for band, freqs in mean_bands_freq.items())
        database.store_multiple_processing_result(prepeared_data)

    def define_stress_level(self, database, mne, pulling_interval, pulling_offset):
        now, pull_start, pull_end = get_boudaries(
            pulling_interval, pulling_offset)
        filters = ('band=(alpha,beta,theta,delta)', 'type=total_band_fraction')
        raw = database.pull_processing_result(filters, pull_start, pull_end)
        data = mne.flatten_data(raw)
        if not all(i for i in data.values()):
            return
        for band_name, band_powers in data.items():
            band_powers = list(map(lambda x: x[1], band_powers))
            if len(band_powers) < 2:
                data[band_name] = band_powers.pop()
            elif len(band_powers) < 3:
                data[band_name] = max(band_powers)
            else:
                data[band_name] = max(moving_avg(band_powers, MA_PERIOD))

        results = [
            ('stress', now, data['beta'] / data['alpha']),
            ('concentration', now, data['alpha'] / (data['delta'] / 4)),
            ('frustration', now, data['theta'] / data['alpha']),
            ('relaxation', now, data['delta'] /
             (data['alpha'] + data['beta'])),
        ]
        database.store_multiple_processing_result(results)
