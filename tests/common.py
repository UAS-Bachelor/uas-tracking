import sys
import os
import time
from multiprocessing import Process
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from services.drone_information import drone_information


def start_server(service, port):
    server = Process(target=service, args=[port])
    server.daemon = True
    server.start()
    time.sleep(1)
    return server


def stop_server(server):
    server.terminate()
    server.join()


def __run_drone_information(port):
    drone_information.app.run(host='127.0.0.1', port=port, debug=False, threaded=False)