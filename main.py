from datetime import timedelta
from time import sleep
from timeloop import Timeloop

from board_session import BoardSession
from database import Database
from globals import *
from gui import GUI
from jobs import store_eeg_data
# from mne_translator import MNETranslator


def main():
    try:
        board = BoardSession()
        timeloop = Timeloop()
        database = Database()
        # mne = MNETranslator()
        # gui = GUI(timeloop=timeloop, database=database)
        timeloop._add_job(
            func=store_eeg_data,
            interval=timedelta(seconds=1),
            board=board,
            database=database
        )

        database.connect()
        board.start_stream()
        timeloop.start()
        while(True):
            sleep(10)
    except (Exception, KeyboardInterrupt) as e:
        timeloop.stop()
        board.stop_stream()
        database.disconect()


if __name__ == '__main__':
    main()
