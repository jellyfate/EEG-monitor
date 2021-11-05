from brainflow.board_shim import BoardIds

# BRAINFLOW SETTINGS
BOARD_ID = BoardIds.GANGLION_BOARD.value
DEVICE_NAME = 'Ganglion-b97c'
DEVICE_MAC_ADDRESS = 'd0:fb:ad:39:31:6d'
DONGLE_PORT = '/dev/ttyACM0'
CHANNELS_NAMES = ['f1', 'f2', 'f3', 'f4']
TIMEOUT = 50

# INFLUXDB SETTINGS
INFLUX_URL = 'http://localhost:8086'
INFLUX_TOKEN = '_OIepEXKmj8b2DxG1zimKF_cYmiXNU2o3CMoPhoEbyDS1WAfKqxng91ztqN1Mn5TsVNVlScqNQHrYr6oIwYM5w=='
INFLUX_ORG = 'local'
INFLUX_BUCKET = "influx1"
