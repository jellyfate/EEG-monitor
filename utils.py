from datetime import datetime

from numpy import cumsum, insert


# define moving average function
def moving_avg(x, n):
    result_cumsum = cumsum(insert(x, 0, 0))
    return (result_cumsum[n:] - result_cumsum[:-n]) / float(n)


def get_boudaries(pulling_interval, pulling_offset):
    now = int(datetime.timestamp(datetime.now()) * 1000)
    pull_start = now - int(pulling_interval.total_seconds() * 1000)
    pull_end = now + int(pulling_offset.total_seconds() * 1000)
    return (now, pull_start, pull_end)
