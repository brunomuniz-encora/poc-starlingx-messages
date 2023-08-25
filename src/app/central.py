"""
Central server functions
"""
import io
import json
import math
import multiprocessing
import statistics
import threading
import time
from collections import defaultdict
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import matplotlib.pyplot as plt

import config
from circulartimeseriesqueue import CircularDictQueue


class CentralRequestHandler(BaseHTTPRequestHandler):
    events = multiprocessing.Queue()
    aggregated_events = CircularDictQueue(100)
    active_clients = defaultdict(str)

    def do_GET(self):
        if self.path.endswith(f'{config.CENTRAL_CLOUD_IMAGE}.png'):
            content = generate_image_graph(self.aggregated_events)

            self.send_response_only(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()

            self.wfile.write(content)
        elif self.path == '/':
            threat_index = generate_metrics(self.aggregated_events)
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
                   '       <h2 id="title">Threat tracker (version: '\
                   '                1.2.2)</h2>\n'\
                   f'       <h4>Threat index: {threat_index}</h4>' \
                   f'       <img id="graph" src="{config.CENTRAL_CLOUD_IMAGE}.png">' \
                   f'       <p>' \
                   f'           {generate_clients_table(self.active_clients)}' \
                   '        </p>'\
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


def generate_metrics(aggregated_events):
    values = aggregated_events
    if len(values.items()) < 1:
        return 0
    warnings_amount = [warnings
                       for _, warnings
                       in sorted(values.items(), key=lambda x: x[0])
                       if warnings is not None]
    return statistics.mean(warnings_amount)


def generate_clients_table(active_clients):
    table_html = '<table>\n'
    table_html += '<tr><th>Client ID</th><th>Client IP</th><th>Version</th></tr>\n'

    for client_id, client_data in active_clients.items():
        client_ip = client_data['clientip']
        version = client_data['version']
        table_html += f'<tr><td>{client_id}</td><td>{client_ip}</td><td>{version}</td></tr>\n'

    table_html += '</table>'
    return table_html


def generate_image_graph(aggregated_events):
    values = aggregated_events
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


def aggregate_data(events, aggregated_events, active_clients, bucket_size):
    while True:
        # Get the amount of nodes with warnings since last read
        warnings = events.qsize()
        data = defaultdict(int)
        active_clients.clear()

        # Dequeue read elements
        for _ in range(0, warnings):
            event = json.loads(events.get())

            # Aggregate event count
            aggregate_timestamp = \
                math.floor(event["datetime"] / bucket_size) * bucket_size
            data[aggregate_timestamp] += 1

            # Set active clients info
            active_clients[event["clientid"]] = {
                'version': event["version"],
                'clientid': event["clientid"],
                'clientip': event["clientip"]
            }

        for key, value in data.items():
            aggregated_events.enqueue(int(key), int(value))

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
                                                  handler_class.aggregated_events,
                                                  handler_class.active_clients,
                                                  bucket_size))

    central_server.start()
    aggregation_service.start()
