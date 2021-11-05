def store_eeg_data(board, mne, database):
    data = board.get_data()
    raw = mne.raw(data)
    database.write(raw)
