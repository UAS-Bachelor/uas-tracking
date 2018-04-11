import time

def epoch_to_datetime(epoch):
    return time.strftime('%d %b %Y, %H:%M:%S', time.localtime(epoch))


def epoch_to_time(epoch):
    return time.strftime('%H:%M:%S', time.gmtime(epoch))