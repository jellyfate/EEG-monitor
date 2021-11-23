from brainflow.board_shim import BoardIds

# BRAINFLOW SETTINGS
BOARD_ID = BoardIds.GANGLION_BOARD.value
DEVICE_NAME = 'Ganglion-b97c'
DEVICE_MAC_ADDRESS = 'd0:fb:ad:39:31:6d'
DONGLE_PORT = '/dev/ttyACM0'
CHANNELS_NAMES = ['f1', 'f2', 'f3', 'f4']
CHANNELS_MAPPING = ['f1', 'f2', 'f3', 'f4',
                    'f5', None, None, None,
                    None, None, None, None,
                    None, 'Timestamp', None]
TIMEOUT = 50

# REDIS SETTINGS
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None

# PROCESSING SETTINGS
FREQ_BANDS = dict(
    delta=(1, 4),
    theta=(4, 8),
    alpha=(7, 13),
    beta=(13, 30),
    gamma=(30, 47)
)
CONDITIONS = ['stress', 'concentration', 'frustration', 'relaxation']
MA_PERIOD = 3
INTERVAL = 1
START_OFFSET = 3
END_OFFSET = 3
