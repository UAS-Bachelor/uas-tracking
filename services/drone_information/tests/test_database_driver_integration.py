import pytest
import sys
import os
import json
from flask import Flask
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from database_driver import Drone, Route, DatabaseDriver
from exceptions import RouteNotFoundException


@pytest.fixture
def drone_data():
    yield {
        'id': '919',
        'name': '000919', 
        'lat': 55.37,
        'lon': 10.43, 
        'alt': 0.00, 
        'time': 1523020346, 
        'time_stamp': '2018-04-06 13:12:26', 
        'sim': 1
    }


@pytest.fixture
def drone(drone_data):
    yield Drone(drone_data)


@pytest.fixture
def db_config():
    __config_file = os.path.join(os.path.dirname(__file__), '../cfg/config.json')
    yield json.load(open(__config_file))['db']


@pytest.fixture
def database_driver(db_config):
    app = Flask(__name__)
    with app.app_context():
        yield DatabaseDriver(app, db_config)


@pytest.fixture
def insert_finished_route(database_driver, drone):
    route = Route(drone_id=drone.id, start_time=drone.time, end_time=drone.time)
    database_driver.add(drone)
    database_driver.add(route)
    database_driver.commit()
    yield route
    database_driver.delete(drone)
    database_driver.delete(route)
    database_driver.commit()


@pytest.fixture
def insert_live_route(database_driver, drone):
    route = Route(drone_id=drone.id, start_time=drone.time, end_time=None)
    database_driver.add(drone)
    database_driver.add(route)
    database_driver.commit()
    yield route
    database_driver.delete(drone)
    database_driver.delete(route)
    database_driver.commit()


@pytest.fixture
def nonexistant_route():
    yield Route(route_id=-1, drone_id=-1, start_time=-1, end_time=-1)


def test_get_live_routes(database_driver, insert_live_route):
    live_routes = database_driver.get_live_routes()
    assert any(route.route_id == insert_live_route.route_id for route in live_routes)


def test_get_data_point_by_live_route(database_driver, drone, insert_live_route):
    retrieved_drone = database_driver.get_data_point_by_live_route(insert_live_route)
    assert retrieved_drone['id'] == drone.id
    assert retrieved_drone['lat'] == drone.lat
    assert retrieved_drone['lon'] == drone.lon
    assert retrieved_drone['alt'] == drone.alt
    assert retrieved_drone['time'] == drone.time


def test_get_route_by_routeid(database_driver, insert_finished_route):
    retrieved_route = database_driver.get_route_by_routeid(insert_finished_route.route_id)
    assert retrieved_route.route_id == insert_finished_route.route_id


def test_get_route_by_routeid_exception(database_driver):
    routeid = -1
    with pytest.raises(RouteNotFoundException) as exception_info:
        database_driver.get_route_by_routeid(routeid)
        assert str(routeid) in exception_info.value


def test_get_route_by_droneid_and_start_time(database_driver, drone, insert_finished_route):
    retrieved_route = database_driver.get_route_by_droneid_and_start_time(drone.id, insert_finished_route.start_time)
    assert retrieved_route == insert_finished_route


def test_get_data_points_by_route(database_driver, drone, insert_finished_route):
    data_points = database_driver.get_data_points_by_route(insert_finished_route)
    retrieved_drone = data_points[0]
    assert retrieved_drone['id'] == drone.id
    assert retrieved_drone['lat'] == drone.lat
    assert retrieved_drone['lon'] == drone.lon
    assert retrieved_drone['alt'] == drone.alt
    assert retrieved_drone['time'] == drone.time


@pytest.mark.filterwarnings('ignore:DELETE')
def test_get_finished_routes(database_driver, drone, insert_finished_route, insert_live_route):
    routes = database_driver.get_finished_routes()
    assert any(route['route_id'] != insert_live_route.route_id for route in routes)
    assert any(route['route_id'] == insert_finished_route.route_id for route in routes)


@pytest.mark.filterwarnings('ignore:DELETE')
def test_delete_data_points_by_route(database_driver, drone, insert_finished_route):
    database_driver.delete_data_points_by_route(insert_finished_route)
    data_points = database_driver.get_data_points_by_route(insert_finished_route)
    assert len(data_points) == 0


def test_drone_creation_from_dict(drone_data):
    drone = Drone(drone_data)
    assert drone.id == drone_data['id']
    assert drone.lat == drone_data['lat']
    assert drone.lon == drone_data['lon']
    assert drone.alt == drone_data['alt']
    assert drone.time == drone_data['time']


if __name__ == '__main__':
    pytest.main()