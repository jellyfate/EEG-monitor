def store_eeg_data(board, database):
    data = board.get_data()
    database.store_eeg(data)
