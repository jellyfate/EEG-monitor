from datetime import timedelta

from timeloop import Timeloop

from board_session import BoardSession
from database import Database
from globals import *
from gui import GUI
from jobs import store_eeg_data
from mne_translator import MNETranslator


def main():
    try:
        timeloop = Timeloop()
        database = Database()
        mne = MNETranslator()
        board = BoardSession()

        board.start_stream()
        timeloop._add_job(
            func=store_eeg_data,
            interval=timedelta(seconds=5),
            board=board,
            mne=mne,
            database=database
        )
        timeloop.start()

        gui = GUI(timeloop, database)
        gui.show()
    except (Exception, KeyboardInterrupt) as e:
        timeloop.stop()
        board.stop_stream()


if __name__ == '__main__':
    main()
