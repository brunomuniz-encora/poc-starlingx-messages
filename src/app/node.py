"""
Distributed nodes functions
"""

import json
import time
from datetime import datetime

import requests

from src.app.utils import random_word, random_number


def send_post_request(url, data):
    headers = {'Content-type': 'application/json'}
    json_data = json.dumps(data)

    response = ""
    try:
        response = requests.post(url, data=json_data, headers=headers)
        if response.status_code == 204:
            print("POST request successful.")
        else:
            print(f"POST request failed. Status code: {response.status_code}")
    except Exception as e:
        print(f'Exception on request to {url}: {e}')


def run_distributed_node(central_url):
    node_id = random_word(5)
    number = random_number(100)
    while True:
        data = {
            "when": datetime.now().timestamp(),
            "who": node_id,
            "how-much": number
        }
        send_post_request(central_url, data)
        time.sleep(1)
