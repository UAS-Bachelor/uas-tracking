import time

def epoch_to_datetime(epoch):
    return time.strftime('%d %b %Y, %H:%M:%S', time.gmtime(epoch)) #time.localtime


def epoch_to_datetime_with_dashes(epoch):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epoch))


def epoch_to_time(epoch):
    return time.strftime('%H:%M:%S', time.gmtime(epoch))
