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
    aggregated_node_events = CircularDictQueue(50)
    aggregated_server_events = CircularDictQueue(50)
    active_clients = defaultdict(str)

    def do_GET(self):
        if self.path.endswith(f'{config.CENTRAL_CLOUD_IMAGE}.png'):
            content = generate_image_graph(self.aggregated_node_events)

            self.send_response_only(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()

            self.wfile.write(content)
        elif self.path.endswith(f'{config.CENTRAL_CLOUD_SERVER_IMAGE}.png'):
            content = generate_image_graph(self.aggregated_server_events)

            self.send_response_only(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()

            self.wfile.write(content)
        elif self.path == '/':
            threat_index = generate_metrics(self.aggregated_node_events)
            self.send_response_only(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html_node_events = '<h4>Accumulated Node Events Timeseries</h4>' \
                   f'       <img id="graph" src="{config.CENTRAL_CLOUD_IMAGE}.png">'

            html_server_events = '<h4>Server Events Timeseries</h4>' \
                   f'       <img id="graph" src="{config.CENTRAL_CLOUD_SERVER_IMAGE}.png">'

            html_clients_table = f'{generate_clients_table(self.active_clients)}'

            html = '<!DOCTYPE html>\n'\
                   '<html>\n'\
                   '   <head>\n'\
                   '       <title>Central Dashboard</title>\n'\
                   '       <meta http-equiv="refresh" content="5">\n'\
                   '   </head>\n'\
                   '   <body>\n'\
                   '       <h2 id="title">Threat tracker (version: '\
                   '                1.4.0)</h2>\n'\
                   f'       <h4>Threat index: {threat_index}</h4>' \
                   f'       {html_node_events}' \
                   f'       {html_clients_table}' \
                   f'       {html_server_events}' \
                   '   </body>\n'\
                   '</html>\n'\

            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        server_date_time = datetime.now().timestamp()

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        json_data = json.loads(post_data)
        json_data['server_datetime'] = server_date_time

        self.send_response_only(204)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        version = json_data['version']
        event_date_time = datetime.fromtimestamp(json_data['datetime'])
        client_id = json_data['clientid']
        client_ip = json_data['clientip']
        threats = json_data['threats']

        print(f"[{server_date_time}: at {event_date_time} from {client_ip}"
              f"/{client_id}] "
              f"Threats amount to {threats}% os scans, which is considered an "
              f"attack in this node's region")

        self.events.put(json_data)

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


def aggregate_data(events, aggregated_events, aggregated_server_events,
                   active_clients, bucket_size):
    while True:
        # Get the number of events on the queue (since last read)
        number_of_events = events.qsize()
        node_events = defaultdict(int)
        server_events = defaultdict(int)
        active_clients.clear()

        # Dequeue read elements
        for _ in range(0, number_of_events):
            event = events.get()

            # Aggregate event count based on event timestamp
            aggregate_timestamp = \
                math.floor(event["datetime"] / bucket_size) * bucket_size
            node_events[aggregate_timestamp] += 1

            # Aggregate event count, but based on server timestamp.
            aggregate_server_timestamp = \
                math.floor(event["server_datetime"] / bucket_size) * bucket_size
            server_events[aggregate_server_timestamp] += 1

            # Set active clients info
            active_clients[event["clientid"]] = {
                'version': event["version"],
                'clientid': event["clientid"],
                'clientip': event["clientip"]
            }

        for key, value in node_events.items():
            aggregated_events.enqueue(int(key), int(value))

        for key, value in server_events.items():
            aggregated_server_events.enqueue(int(key), int(value))


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
                                                  handler_class.aggregated_node_events,
                                                  handler_class.aggregated_server_events,
                                                  handler_class.active_clients,
                                                  bucket_size))

    central_server.start()
    aggregation_service.start()
