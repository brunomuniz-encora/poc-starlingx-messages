"""
Distributed nodes functions
"""
import io
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import matplotlib.pyplot as plt

import requests
import utils
import config
from circulartimeseriesqueue import CircularTimeseriesDict


class NodeRequestHandler(BaseHTTPRequestHandler):
    circular_queue = CircularTimeseriesDict(100)
    threshold = 20

    def do_GET(self):
        if self.path.endswith(f'{config.NODE_IMAGE}.png'):
            content = generate_image_graph(self.circular_queue, self.threshold)

            self.send_response_only(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()

            self.wfile.write(content)
        elif self.path == '/':
            self.send_response_only(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html =   '<!DOCTYPE html>\n'
            html +=  '<html>\n'
            html +=  '   <head>\n'
            html +=  '       <title>Node Dashboard</title>\n'
            html +=  '       <meta http-equiv="refresh" content="5">\n'
            html +=  '   </head>\n'
            html +=  '   <body>\n'
            html +=  f'       <h2 id="title">Local scans</h2>\n'
            html += f'       <img id="graph" src="{config.NODE_IMAGE}.png">\n'
            html +=  '   </body>\n'
            html +=  '</html>\n'

            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()


def send_post_request(url, data):
    headers = {'Content-type': 'application/json'}
    json_data = json.dumps(data)

    try:
        response = requests.post(url, data=json_data, headers=headers, timeout=30)
        if response.status_code != 204:
            print(f'POST request failed. Status code: {response.status_code}')
    except Exception as exception:
        print(f'Exception on request to {url}: {exception}')


def generate_image_graph(circular_queue, to_server_threshold):
    values = circular_queue
    date_time = [float(timestamp)
                 for timestamp, _ in sorted(values.items(), key=lambda x: x[0])
                 if timestamp is not None]
    threats = [scans for _, scans in sorted(values.items(), key=lambda x: x[0])
               if scans is not None]

    plt.plot(date_time, threats, color='blue')
    plt.xlabel('Date time (timestamp)')
    plt.ylabel('Threats percentage (%)')
    plt.axhline(y=to_server_threshold,
                color='r',
                label='Above this line, notify Central Cloud')
    plt.legend()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    image_bugger = buffer.getvalue()

    buffer.close()
    plt.clf()

    return image_bugger


def run_node_image_server(local_server_class, handler_class, port):
    local_server_address = ('', port)
    httpd = local_server_class(local_server_address, handler_class)
    print(f'Starting HTTP listener on port {port}...')
    httpd.serve_forever()


def run_node_service(central_url, circular_queue, to_server_threshold=20,
                     scan_frequency=2):
    client_id = utils.random_word(5)
    client_ip = utils.get_ip()

    while True:
        threats = utils.random_percentage_long_tail_distribution()
        print(f'[{datetime.now()} {client_ip}/{client_id} v{config.VERSION}] ' +
              f'Scans with threats: {threats}%')

        now = datetime.now().timestamp()
        data = {
            'version': config.VERSION,
            'datetime': now,
            'clientid': client_id,
            'clientip': client_ip,
            'threats': threats
        }
        circular_queue.enqueue(now, threats)

        if threats > to_server_threshold:
            send_post_request(central_url, data)

        time.sleep(scan_frequency)


def run_distributed_node(central_url,
                         local_server_class=HTTPServer,
                         port=8001,
                         to_server_threshold=20,
                         scan_frequency=2):

    handler_class = NodeRequestHandler
    handler_class.circular_queue = CircularTimeseriesDict(100)
    handler_class.threshold = to_server_threshold

    image_server = threading.Thread(target=run_node_image_server,
                                    args=(local_server_class, handler_class, port))
    service = threading.Thread(target=run_node_service,
                               args=(central_url, handler_class.circular_queue,
                                     to_server_threshold, scan_frequency))


    image_server.start()
    service.start()
