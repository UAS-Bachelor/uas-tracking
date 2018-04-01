#!/usr/bin/python
import requests
import time


def send_log_entry(log):
    r = requests.post("https://droneid.dk/bsc2018/droneid_log.php", data={
                      'aid': log['aid'], 'lat': log['lat'], 'lon': log['lon'], 'alt': log['alt']})
    print(r.status_code, r.reason)
    print(r.text)


LOG_TEST_DATA = [
    {
        'aid': 911,
        'lat': 55.37000,
        'lon': 10.43000,
        'alt': 49.75,
    },
    {
        'aid': 911,
        'lat': 55.38000,
        'lon': 10.43000,
        'alt': 49.75,
    },
    {
        'aid': 911,
        'lat': 55.39000,
        'lon': 10.44000,
        'alt': 49.75,
    },
    {
        'aid': 911,
        'lat': 55.40000,
        'lon': 10.45000,
        'alt': 49.75,
    },
    {
        'aid': 911,
        'lat': 55.41000,
        'lon': 10.46000,
        'alt': 49.75,
    },
    {
        'aid': 911,
        'lat': 55.41000,
        'lon': 10.47000,
        'alt': 49.75,
    },
    {
        'aid': 911,
        'lat': 55.41000,
        'lon': 10.48000,
        'alt': 49.75,
    },
    {
        'aid': 911,
        'lat': 55.42000,
        'lon': 10.48000,
        'alt': 49.75,
    },
    {
        'aid': 911,
        'lat': 55.43000,
        'lon': 10.48000,
        'alt': 49.75,
    }, 
    {
        'aid': 911,
        'lat': 55.44000,
        'lon': 10.48000,
        'alt': 49.75,
    }
]

for i in range(10):
    print('Sending {}'.format(i))
    send_log_entry(LOG_TEST_DATA[i])
    time.sleep(5)

#send_log_entry(LOG_TEST_DATA[0])
#send_log_entry(LOG_TEST_DATA[1])
