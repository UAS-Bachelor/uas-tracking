import os
import pytest
import unittest
from models import Drone
import drone_information


@pytest.fixture
def client():
    drone_information.app.config['TESTING'] = True
    client = drone_information.app.test_client()
    yield client

def test_routes_post(client):
    response = client.post('/routes', json=
                    [{
                      'id': 910, 
                      'lat': 55.37000, 
                      'lon': 10.43000, 
                      'alt': 00.00000, 
                      'time': 1524231287
                    }, 
                    {
                      'id': 910, 
                      'lat': 55.38050,
                      'lon': 10.43000,
                      'alt': 100.00000,
                      'time': 1524231299
                    }])
    print('Id {} drone'.format(response.data.decode()))
    print(response.data.decode().strip() == '196')
    print(int(response.data.decode()) == 196)





'''class DroneInformationTestCase(unittest.TestCase):

    def setUp(self):
        drone_information.app.testing = True
        self.app = drone_information.app.test_client()


    def test_stuff(self):
        response = self.app.get('/live')
        print('hi')
        print(response.data.decode())


if __name__ == '__main__':
    unittest.main()'''