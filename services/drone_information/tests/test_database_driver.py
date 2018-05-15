import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from database_driver import Drone

@pytest.fixture(scope='module')
def drone_data():
    yield {
        'id': '910',
        'lat': 55.37,
        'lon': 10.43, 
        'time': 1523020346
    }


def test_drone_creation_from_dict(drone_data):
    drone = Drone(drone_data)
    assert drone.id == drone_data['id']
    assert drone.lat == drone_data['lat']
    assert drone.lon == drone_data['lon']
    assert drone.time == drone_data['time']


if __name__ == '__main__':
    pytest.main()