import pytest
from services.app import app
from services.drone_information import drone_information
from util import config
from multiprocessing import Process


@pytest.fixture
def app_client():
    app.app.config['TESTING'] = True
    app_client = app.app.test_client()
    yield app_client


def test_drone_information_integration(app_client):
    response = app_client.get('/routes')
    assert response.status_code == 503
    assert response.data.decode().strip() == 'Drone information service unavailable'

    server = Process(target=start_drone_information_server, args=[config['drone_information']['port']])
    server.start()
    
    response = app_client.get('/routes')
    assert response.status_code == 200

    server.terminate()
    server.join()


def test_different_ports_for_same_service(app_client):
    server = Process(target=start_drone_information_server, args=[config['drone_information']['port']])
    server.start()
    
    response = app_client.get('/routes')
    assert response.status_code == 200

    server.terminate()
    server.join()

    new_port = 6001
    server = Process(target=start_drone_information_server, args=[new_port])
    server.start()
    
    app.config = {
        'drone_information': {
            'host': '127.0.0.1', 
            'port': new_port
        }
    }
    response = app_client.get('/routes')
    assert response.status_code == 200

    server.terminate()
    server.join()


def start_drone_information_server(port):
    drone_information.app.run(host='127.0.0.1', port=port, threaded=True)


if __name__ == '__main__':
    pytest.main()