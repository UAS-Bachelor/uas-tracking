import requests
import time
import argparse
import json
import MySQLdb

__config_file = 'cfg/config.json'
config = json.load(open(__config_file))
dbconfig = config['db']

droneurl = config['droneurl']

db = MySQLdb.connect(host=dbconfig['host'], port=dbconfig['port'],
                     user=dbconfig['user'], password=dbconfig['password'], db=dbconfig['database'])
cursor = db.cursor()

previous_result = [None]


def get_drone_info():
    list_of_drone_dicts = []
    drone_info = requests.get(droneurl).text.strip('\n')
    if drone_info:
        for row in drone_info.splitlines():
            data = row.split(',')
            list_of_drone_dicts.append({
                'time_stamp': data[0],
                'time': data[1],
                'id': data[2],
                'name': data[3],
                'lat': data[4],
                'lon': data[5],
                'alt': data[6],
                'acc': data[7],
                'fix': data[8],
                'lnk': data[9],
                'eng': data[10],
                'sim': data[11]
            })
    return list_of_drone_dicts


def store_row_drone_info(drone_dict):
    placeholder_values = ', '.join(['%s'] * len(drone_dict))
    columns = ', '.join(drone_dict.keys())
    sql = "INSERT IGNORE INTO %s ( %s ) VALUES ( %s )" % (
        'drone', columns, placeholder_values)
    cursor.execute(sql, drone_dict.values())


def store_drone_info(drone_list):
    for drone_dict in drone_list:
        store_row_drone_info(drone_dict)


def get_and_store_drone_info():
    result = get_drone_info()
    global previous_result
    pairs = zip(result, previous_result)
    if any(x != y for x, y in pairs):
        store_drone_info(result)
    previous_result = result


if __name__ == '__main__':
    print('Monitor droneid and log drone positions to drone_information database')
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delay', type=int, default=15,
                        help='time (in seconds) between each log')
    args = parser.parse_args()
    while True:
        get_and_store_drone_info()
        time.sleep(args.delay)
