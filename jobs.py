from globals import *
from mne_translator import MNETranslator
from utils import get_boudaries, moving_avg


def store_eeg_data(board, database):
    data = board.get_data()
    database.store_eeg(data)


def define_bands(database, mne, pulling_interval, pulling_offset):
    now, pull_start, pull_end = get_boudaries(pulling_interval, pulling_offset)
    data = mne._flatten_data(database.pull_eeg(pull_start, pull_end))
    if not all(i for i in data.values()):
        return

    result = []
    total_bands_power = {band: 0.0 for band in FREQ_BANDS}
    for channel_name, channel_data in data.items():
        if channel_name == 'f1':
            continue
        data = list(map(lambda x: x[1], channel_data))
        bands_power = mne.get_bandpower(data, FREQ_BANDS)
        for band_name, band_power in bands_power.items():
            total_bands_power[band_name] += band_power
            result.append((f'{channel_name}-{band_name}', now, band_power))
    result.extend((band, now, power)
                  for band, power in total_bands_power.items())
    database.store_multiple_processing_result(result)


def define_stress_level(database, mne, pulling_interval, pulling_offset):
    now, pull_start, pull_end = get_boudaries(pulling_interval, pulling_offset)
    filters = ('band=(alpha,beta,theta,delta)', 'type=total_band_fraction')
    raw = database.pull_processing_result(filters, pull_start, pull_end)
    data = mne._flatten_data(raw)
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
        ('relaxation', now, data['delta'] / (data['alpha'] + data['beta'])),
    ]
    database.store_multiple_processing_result(results)
