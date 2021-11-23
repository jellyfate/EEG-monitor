from board_session import BoardSession
from database import Database
from globals import *
from jobs import JobManager
from mne_translator import MNETranslator


class Main:
    def __init__(self):
        self.board = BoardSession()
        self.database = Database()
        self.mne = MNETranslator()
        self.job_manager = JobManager(self.board, self.database, self.mne)

    def run(self):
        try:
            self.database.connect()
            self.board.start_stream()
            self.job_manager.start_jobs()
        except (KeyboardInterrupt, SystemExit):
            self.board.stop_stream()
            self.database.disconect()


if __name__ == '__main__':
    try:
        main = Main()
        main.run()
    except BaseException as e:
        print(repr(e))
