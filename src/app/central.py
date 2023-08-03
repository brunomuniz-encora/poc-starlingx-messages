"""
Central server functions
"""
import io
import json
import math
import multiprocessing
import threading
import time
from collections import defaultdict
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import matplotlib.pyplot as plt

import config
from circulartimeseriesqueue import CircularTimeseriesDict


class CentralRequestHandler(BaseHTTPRequestHandler):
    events = multiprocessing.Queue()
    circular_queue = CircularTimeseriesDict(100)

    def do_GET(self):
        if self.path.endswith(f'{config.CENTRAL_CLOUD_IMAGE}.png'):
            content = generate_image_graph(self.circular_queue)

            self.send_response_only(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()

            self.wfile.write(content)
        elif self.path == '/':
            self.send_response_only(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = '<!DOCTYPE html>\n'\
                   '<html>\n'\
                   '   <head>\n'\
                   '       <title>Central Dashboard</title>\n'\
                   '       <meta http-equiv="refresh" content="5">\n'\
                   '   </head>\n'\
                   '   <body>\n'\
                   '       <h2 id="title">Threat tracker</h2>\n'\
                   '       <img id="graph" src="' \
                   f'{config.CENTRAL_CLOUD_IMAGE}.png">\n'\
                   '   </body>\n'\
                   '</html>\n'\

            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

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

        self.events.put(post_data)

        response = {'message': 'Received POST data successfully',
                    'data': json_data}
        self.wfile.write(json.dumps(response).encode('utf-8'))


def generate_image_graph(circular_queue):
    values = circular_queue
    date_time = [float(timestamp)
                 for timestamp, _ in sorted(values.items(), key=lambda x: x[0])
                 if timestamp is not None]
    warnings_amount = [warnings
                       for _, warnings
                       in sorted(values.items(), key=lambda x: x[0])
                       if warnings is not None]

    plt.plot(date_time, warnings_amount, color='blue')
    plt.xlabel('Date time (timestamp)')
    plt.ylabel('Warnings')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    image_buffer = buffer.getvalue()

    buffer.close()
    plt.clf()

    return image_buffer


def aggregate_data(events, circular_queue, bucket_size):
    while True:
        # Get the amount of nodes with warnings since last read
        warnings = events.qsize()
        data = defaultdict(int)

        # Dequeue read elements
        for _ in range(0, warnings):
            event = json.loads(events.get())
            aggregate_timestamp = math.floor(event["datetime"] / (
                    bucket_size)) * bucket_size
            data[aggregate_timestamp] += 1

        for key, value in data.items():
            circular_queue.enqueue(int(key), int(value))

        time.sleep(bucket_size)


def run_central_server(server_class, handler_class, port):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting HTTP listener on port {port}...')
    httpd.serve_forever()


def run_central_cloud(server_class=HTTPServer,
                      handler_class=CentralRequestHandler,
                      port=8000,
                      bucket_size=1):
    central_server = threading.Thread(target=run_central_server,
                                           args=(server_class, handler_class, port))
    aggregation_service = threading.Thread(target=aggregate_data,
                                            args=(handler_class.events,
                                                  handler_class.circular_queue,
                                                  bucket_size))

    central_server.start()
    aggregation_service.start()
