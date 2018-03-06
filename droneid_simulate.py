#!/usr/bin/python

import requests


def send_log_entry(log):
    r = requests.post("https://droneid.dk/bsc2018/droneid_log.php", data={
                      'aid': log['aid'], 'lat': log['lat'], 'lon': log['lon'], 'alt': log['alt']})
    print(r.status_code, r.reason)
    print(r.text)


LOG_TEST_DATA = [
    {
        'aid': 910,
        'lat': 55.37000,
        'lon': 10.43000,
        'alt': 49.75,
    },
]

send_log_entry(LOG_TEST_DATA[0])
