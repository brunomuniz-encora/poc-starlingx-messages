"""
Distributed nodes functions
"""

import json
import time
import multiprocessing
from http.server import HTTPServer
from datetime import datetime
import matplotlib.pyplot as plt

import requests
import utils
import config
from circularqueue import CircularQueue
from httprequests import RequestHandler

def send_post_request(url, data):
    headers = {'Content-type': 'application/json'}
    json_data = json.dumps(data)

    try:
        response = requests.post(url, data=json_data, headers=headers, timeout=30)
        if response.status_code != 204:
            print(f'POST request failed. Status code: {response.status_code}')
    except Exception as exception:
        print(f'Exception on request to {url}: {exception}')


def generate_image_graph(circular_queue):
    values = circular_queue.get_items()
    date_time = [value['datetime'] for value in values if value is not None]
    threats = [value['threats'] for value in values if value is not None]

    plt.plot(date_time, threats, color='blue')
    plt.xlabel('Date time (timestamp)')
    plt.ylabel('Threats percentage (%)')
    plt.axhline(y=config.TO_CENTRAL_CLOUD_TRESHOLD,
                color='r',
                label='Above this line, notify Central Cloud')
    plt.legend()
    plt.savefig(f'{config.NODE_IMAGE}.png')
    plt.clf()


def run_node_image_server(local_server_class, handler_class, port):
    local_server_address = ('', port)
    handler_class.image_name = config.NODE_IMAGE
    httpd = local_server_class(local_server_address, handler_class)
    print(f'Starting HTTP listener on port {port}...')
    httpd.serve_forever()


def run_node_service(central_url):
    client_id = utils.random_word(5)
    client_ip = utils.get_ip()
    circular_queue = CircularQueue(100)

    while True:
        threats = utils.random_percentage_long_tail_distribution()
        print(f'[{datetime.now()} {client_ip}/{client_id} v{config.VERSION}] ' +
              f'Scans with threats: {threats}%')

        data = {
            'version': config.VERSION,
            'datetime': datetime.now().timestamp(),
            'clientid': client_id,
            'clientip': client_ip,
            'threats': threats
        }
        circular_queue.enqueue(data)
        generate_image_graph(circular_queue)

        if threats > config.TO_CENTRAL_CLOUD_TRESHOLD:
            send_post_request(central_url, data)

        time.sleep(1)


def run_distributed_node(central_url,
                         local_server_class=HTTPServer,
                         handler_class=RequestHandler,
                         port=8001):
    image_server = multiprocessing.Process(target=run_node_image_server,
                                           args=(local_server_class, handler_class, port))
    service = multiprocessing.Process(target=run_node_service, args=(central_url,))


    image_server.start()
    service.start()
