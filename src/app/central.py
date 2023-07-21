"""
Central server functions
"""

import json
import time
import multiprocessing
from datetime import datetime
from http.server import HTTPServer
from queue import Empty
import matplotlib.pyplot as plt

import config
from circularqueue import CircularQueue
from httprequests import RequestHandler


class CentralRequestHandler(RequestHandler):
    queue = multiprocessing.Queue()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        json_data = json.loads(post_data)

        self.send_response_only(204)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        version = json_data['version']
        date_time = datetime.fromtimestamp(json_data['datetime'])
        client_id = json_data['clientid']
        client_ip = json_data['clientip']
        threats = json_data['threats']

        print(f"[{date_time} {client_ip}/{client_id} v{version}] " +
              f"Threats amount {threats}%, an attack is happening in this node region")

        self.queue.put(post_data)

        response = {'message': 'Received POST data successfully',
                    'data': json_data}
        self.wfile.write(json.dumps(response).encode('utf-8'))


def generate_image_graph_every_second(nodes_notification_queue):
    circular_queue = CircularQueue(100)

    while True:
        #get the amount of nodes with warnings on the last second
        warnings = nodes_notification_queue.qsize()

        #remove readed elements from queue
        for _ in range(0, warnings):
            nodes_notification_queue.get()

        data = {
            'datetime': datetime.now().timestamp(),
            'warningsamount': warnings
        }
        circular_queue.enqueue(data)

        values = circular_queue.get_items()
        date_time = [value['datetime'] for value in values if value is not None]
        warnings_amount = [value['warningsamount'] for value in values if value is not None]

        plt.plot(date_time, warnings_amount, color='blue')
        plt.xlabel('Date time (timestamp)')
        plt.ylabel('Nodes with warnings')
        plt.savefig(f'{config.CENTRAL_CLOUD_IMAGE}.png')
        plt.clf()

        time.sleep(1)


def run_central_server(server_class, handler_class, port):
    server_address = ('', port)
    handler_class.image_name = config.CENTRAL_CLOUD_IMAGE
    httpd = server_class(server_address, handler_class)
    print(f'Starting HTTP listener on port {port}...')
    httpd.serve_forever()

def run_central_cloud(server_class=HTTPServer,
                      handler_class = CentralRequestHandler,
                      port=8000):
    central_server = multiprocessing.Process(target=run_central_server,
                                           args=(server_class, handler_class, port))
    image_service = multiprocessing.Process(target=generate_image_graph_every_second,
                                            args=(handler_class.queue,))

    central_server.start()
    image_service.start()
