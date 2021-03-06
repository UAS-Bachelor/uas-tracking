#!/usr/bin/python
import requests
import time


def send_log_entry(log):
    r = requests.post("https://droneid.dk/bsc2018/droneid_log.php", data={
                      'aid': log['aid'], 'lat': log['lat'], 'lon': log['lon'], 'alt': log['alt']})
    print(r.status_code, r.reason)
    #print(r.text)


LOG_TEST_DATA = [
    {
        'aid': 912,
        'lat': 55.47000,
        'lon': 10.48000,
        'alt': 100.00000,
    },
    {
        'aid': 913,
        'lat': 55.47050,
        'lon': 10.48000,
        'alt': 100.00000,
    },
    {
        'aid': 914,
        'lat': 55.47025,
        'lon': 10.48025,
        'alt': 100.00000,
    },
    {
        'aid': 911,
        'lat': 55.40000,
        'lon': 10.45000,
        'alt': 500.00000,
    },
    {
        'aid': 911,
        'lat': 55.41000,
        'lon': 10.46000,
        'alt': 700.00000,
    },
    {
        'aid': 911,
        'lat': 55.41000,
        'lon': 10.47000,
        'alt': 600.00000,
    },
    {
        'aid': 911,
        'lat': 55.41000,
        'lon': 10.48000,
        'alt': 400.00000,
    },
    {
        'aid': 911,
        'lat': 55.42000,
        'lon': 10.48000,
        'alt': 300.00000,
    },
    {
        'aid': 911,
        'lat': 55.43000,
        'lon': 10.48000,
        'alt': 200.00000,
    }, 
    {
        'aid': 911,
        'lat': 55.44000,
        'lon': 10.48000,
        'alt': 100.00000,
    }
]

LOG_TEST_DATA2 = [
    {
        'aid': 912,
        'lat': 55.37000,
        'lon': 10.44000,
        'alt': 00.00000,
    },
    {
        'aid': 912,
        'lat': 55.37000,
        'lon': 10.44000,
        'alt': 00.00000,
    },
    {
        'aid': 912,
        'lat': 55.37000,
        'lon': 10.44000,
        'alt': 00.00000,
    },
    {
        'aid': 912,
        'lat': 55.37000,
        'lon': 10.44000,
        'alt': 00.00000,
    },
    {
        'aid': 912,
        'lat': 55.37000,
        'lon': 10.44000,
        'alt': 00.00000,
    },
    {
        'aid': 912,
        'lat': 55.37000,
        'lon': 10.44000,
        'alt': 00.00000,
    },
    {
        'aid': 912,
        'lat': 55.37000,
        'lon': 10.44000,
        'alt': 00.00000,
    },
    {
        'aid': 912,
        'lat': 55.37000,
        'lon': 10.44000,
        'alt': 00.00000,
    },
    {
        'aid': 912,
        'lat': 55.37000,
        'lon': 10.44000,
        'alt': 00.00000,
    },
    {
        'aid': 912,
        'lat': 55.37000,
        'lon': 10.44000,
        'alt': 00.00000,
    },
    {
        'aid': 912,
        'lat': 55.37000,
        'lon': 10.44000,
        'alt': 00.00000,
    }
]




def test_drone_information_post(log):
    #print(requests.get('https://www.techgen.dk/msc/droneTL_1.JSON').text)
    '''r = requests.post("http://127.0.0.1:5001/routes", data=
                      requests.get('https://www.techgen.dk/msc/droneTL_1.JSON').text)'''
    r = requests.post("http://127.0.0.1:5001/routes", json=
                    [{
                      'aid': log['aid'], 
                      'lat': log['lat'], 
                      'lon': log['lon'], 
                      'alt': log['alt'], 
                      'time': 1524231287
                    }, 
                    {
                      'aid': log['aid'], 
                      'lat': log['lat'], 
                      'lon': log['lon'], 
                      'alt': log['alt'], 
                      'time': 1524231299
                    }])
    print(r.status_code, r.reason, r.text)


#test_drone_information_post(LOG_TEST_DATA[1])

for i in range(10):
    print('Sending {}'.format(i))
    send_log_entry(LOG_TEST_DATA[i])
#    send_log_entry(LOG_TEST_DATA2[i])
    time.sleep(2)
'''
r = requests.put("http://127.0.0.1:5001/routes/2470", json=
                    [{
                      'aid': LOG_TEST_DATA2[0]['aid'], 
                      'lat': LOG_TEST_DATA2[0]['lat'], 
                      'lon': LOG_TEST_DATA2[0]['lon'], 
                      'alt': LOG_TEST_DATA2[0]['alt'], 
                      'time': 1526817898
                    }, 
                    {
                      'aid': LOG_TEST_DATA2[1]['aid'], 
                      'lat': LOG_TEST_DATA2[1]['lat'], 
                      'lon': LOG_TEST_DATA2[1]['lon'], 
                      'alt': LOG_TEST_DATA2[1]['alt'], 
                      'time': 1526818900
                    }])
print(r.status_code, r.reason, r.text)
'''