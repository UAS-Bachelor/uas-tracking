import requests
import time
import argparse
import json
import MySQLdb

__config_file = 'cfg/config.json'
config = json.load(open(__config_file))
db_config = config['db']

db = MySQLdb.connect(host=db_config['host'], port=db_config['port'],
                     user=db_config['user'], password=db_config['password'], db=db_config['database'])
cursor = db.cursor()

drones_table = db_config['drones_table']
routes_table = db_config['routes_table']

droneurl = config['droneurl']

buffer = config['buffer']

previous_result = []
gone_drones_buffer = {}


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
    sql = 'INSERT IGNORE INTO {} ( {} ) VALUES ( {} )'.format(
        table, columns, placeholder_values
    )
    cursor.execute(sql, drone_dict.values())


# example usage update_row('routes', {'end_time': '1594329'}, {'id': '914'})
def update_row(table, set_dict, where_dict):
    set_column = __flatten_dict(', ', set_dict)
    where_column = __flatten_dict(' AND ', where_dict)
    sql = 'UPDATE {} SET {} WHERE route_id=(SELECT * FROM (SELECT route_id FROM routes WHERE end_time IS NULL AND {} ORDER BY route_id ASC LIMIT 1) AS a)'.format(table, set_column, where_column)
    cursor.execute(sql)


def __flatten_dict(join_string, dict_to_flat):
    return join_string.join('{!s}={!s}'.format(key, val) for (key, val) in dict_to_flat.items())


def store(table, drone_list):
    for drone_dict in drone_list:
        store_row(table, drone_dict)


def update(table, set_list, where_list):
    for set_dict, where_dict in zip(set_list, where_list):
        update_row(table, set_dict, where_dict)


def get_and_store_drone_info():
    result = get_drone_info()
    global previous_result
    global gone_drones_buffer
    new_drones = []  # De her lists af drone dicts skal gemmes i henholdsvis routes_start og routes_end i DBen
    
    drone_pairs = zip(result, previous_result)

    print('prev {}'.format(previous_result))
    print('result {}'.format(result))

    if not previous_result or not result or any(new_drone != old_drone for new_drone, old_drone in drone_pairs): #Checks the previous result was empty OR if there are any new entries (compared to previous result)
        store(drones_table, result)
        print('Storing...')

        #for hver drone i result, for hver item i dronen's item (id=922, time=15..., lat=55), hvis det id og value IKKE findes i previous_result, så har vi en ny drone
        '''for new_drone in result:

            for key, value in new_drone.items():
                if key not in previous_result:#skal være den enkelte drone, hvilket previous_result er en liste af
                    print(key + ' not in previous result')
                    print(previous_result)'''
            
        for new_drone in result:
            # Finds new IDs, which weren't in the previous result (routes_start)
            if not any(old_drone['id'] == new_drone['id'] for old_drone in previous_result):
                if new_drone['id'] in gone_drones_buffer.keys():
                    print('Rediscovered drone {}'.format(new_drone['id']))
                    gone_drones_buffer.pop(new_drone['id'], None)
                else:
                    new_drones.append({
                        'drone_id': new_drone['id'],
                        'start_time': new_drone['time']
                    })
                    print('New drone: {}'.format(new_drone['id']))
        store(routes_table, new_drones)
        
        for old_drone in previous_result:
            # Finds missing IDs, which are not in the new results (routes_end)
            if not any(new_drone['id'] == old_drone['id'] for new_drone in result):
                gone_drones_buffer[old_drone['id']] = old_drone['time']
                
                print('Gone drone: {}'.format(old_drone['id']))
        #update(routes_table, gone_drones_time, gone_drones_id)

        print('{} gone drones'.format(len(gone_drones_buffer)))
        for gone_drone_id, last_seen in list(gone_drones_buffer.items()):
            if (int(time.time()) - int(last_seen)) > buffer:
                update(routes_table, [{'end_time': last_seen}], [{'drone_id': gone_drone_id}])
                #del gone_drones_buffer[gone_drone_id]
                gone_drones_buffer.pop(gone_drone_id, None)
                print('{} finished its route'.format(gone_drone_id))
    previous_result = result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delay', type=int, default=2,
                        help='time (in seconds) between each log')
    args = parser.parse_args()
    print('Monitor droneid and log drone positions to drone_information database (delay={})'.format(args.delay))
    while True:
        get_and_store_drone_info()
        time.sleep(args.delay)
