"""
Distributed nodes functions
"""

import json
import time
from datetime import datetime

import requests
from app import utils, config


def send_post_request(url, data):
    headers = {'Content-type': 'application/json'}
    json_data = json.dumps(data)

    try:
        response = requests.post(url, data=json_data, headers=headers, timeout=30)
        if response.status_code != 204:
            print(f"POST request failed. Status code: {response.status_code}")
    except Exception as exception:
        print(f'Exception on request to {url}: {exception}')


def run_distributed_node(central_url):
    client_id = utils.random_word(5)
    client_ip = utils.get_ip()

    while True:
        threats = utils.random_percentage_long_tail_distribution()
        print(f"[{datetime.now()} {client_ip}/{client_id} v{config.VERSION}] " +
              f"Scans with threats: {threats}%")

        if threats > config.TO_CENTRAL_CLOUD_TRESHOLD:
            data = {
                "version": config.VERSION,
                "datetime": datetime.now().timestamp(),
                "clientid": client_id,
                "clientip": client_ip,
                "threats": threats
            }
            send_post_request(central_url, data)

        time.sleep(1)
