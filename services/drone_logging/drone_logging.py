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

previous_result = []


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


def store_row(table, drone_dict):
    placeholder_values = ', '.join(['%s'] * len(drone_dict))
    columns = ', '.join(drone_dict.keys())
    sql = "INSERT IGNORE INTO %s ( %s ) VALUES ( %s )" % (
        table, columns, placeholder_values)
    cursor.execute(sql, drone_dict.values())


def store(table, drone_list):
    for drone_dict in drone_list:
        store_row(table, drone_dict)


def get_and_store_drone_info():
    result = get_drone_info()
    global previous_result
    new_drones = [] #De her lists af drone dicts skal gemmes i henholdsvis routes_start og routes_end i DBen
    gone_drones = []
    drone_pairs = zip(result, previous_result)

    if not previous_result or any(new_drone != old_drone for new_drone, old_drone in drone_pairs): #Checks the previous result was empty OR if there are any new entries (compared to previous result)
        store('drones', result)
        for new_drone in result:
            if not any(old_drone['id'] == new_drone['id'] for old_drone in previous_result): #Finds new IDs, which weren't in the previous result (routes_start)
                new_drones.append({
                    'id': new_drone['id'], 
                    'start_time': new_drone['time']
                })
                print('New drone: {}'.format(new_drone['id']))
        store('routes_start', new_drones)

        for old_drone in previous_result:
            if not any(new_drone['id'] == old_drone['id'] for new_drone in result): #Finds missing IDs, which are not in the new results (routes_end)
                gone_drones.append({
                    'id': old_drone['id'], 
                    'end_time': old_drone['time']
                })
                print('Gone drone: {}'.format(old_drone['id']))
        store('routes_end', gone_drones)

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
