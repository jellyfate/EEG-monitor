from datetime import timedelta
from time import sleep

from timeloop import Timeloop

from board_session import BoardSession
from database import Database
from globals import *
from jobs import *
from mne_translator import MNETranslator


def main():
    try:
        board = BoardSession()
        timeloop = Timeloop()
        database = Database()
        mne = MNETranslator()

        timeloop._add_job(
            func=store_eeg_data,
            interval=timedelta(seconds=1),
            database=database,
            board=board
        )
        timeloop._add_job(
            func=define_bands,
            interval=timedelta(seconds=1),
            database=database,
            mne=mne,
            pulling_interval=timedelta(seconds=3),
            pulling_offset=timedelta(seconds=3)
        )
        timeloop._add_job(
            func=define_stress_level,
            interval=timedelta(seconds=1),
            database=database,
            mne=mne,
            pulling_interval=timedelta(seconds=5),
            pulling_offset=timedelta(seconds=5)
        )
    except BaseException as e:
        print(repr(e))

    try:
        database.connect()
        board.start_stream()
        timeloop.start()
        while(True):
            sleep(10)
    except (KeyboardInterrupt, SystemExit):
        timeloop.stop()
        board.stop_stream()
        database.disconect()


if __name__ == '__main__':
    main()
