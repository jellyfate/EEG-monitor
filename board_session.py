from brainflow.board_shim import BoardIds, BoardShim, BrainFlowInputParams

from globals import *


class BoardSession:
    def __init__(self):
        params = BrainFlowInputParams()
        params.mac_address = DEVICE_MAC_ADDRESS
        params.serial_port = DONGLE_PORT
        params.timeout = TIMEOUT
        self.board = BoardShim(BOARD_ID, params)

    def start_stream(self):
        self.board.prepare_session()
        self.board.start_stream()

    def stop_stream(self):
        self.board.stop_stream()
        self.board.release_session()

    def get_data(self):
        return self.board.get_board_data()
