"""
Central server functions
"""

import json
import os
import shutil
import signal
import sys
import threading

from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class DefaultCentralRequestHandler(BaseHTTPRequestHandler):

    class ServerInfo:
        accumulator = []
        nodes = set()

    def generate_html(self, server_data):
        html = '''<html>
          <head>
            <title>HTML in 10 Simple Steps or Less</title>
            <meta http-equiv="refresh" content="5"> <!-- See the difference? -->
          </head>
          <body>'''
        html = f'{html}\n<b>TOTAL: {len(server_data.accumulator)}</b> <br>'

        html = f'{html}\n<p><b>Nodes ({len(server_data.nodes)}): </b><br>'
        for node in server_data.nodes:
            html = f'{html} \n- {node}<br>'

        html = (f'{html}'
                f'  </body>'
                f'</html>')

        return html

    mem = ServerInfo()

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == '/download':
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.send_header('Content-Disposition',
                             'attachment; filename="timeseries.png"')
            self.end_headers()
            path = generate_chart(self.mem)

            with open(path, 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = self.generate_html(self.mem)
            self.wfile.write(bytearray(html, encoding='utf-8'))

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

        self.mem.accumulator.append(threats)

        response = {'message': 'Received POST data successfully',
                    'data': json_data}
        self.wfile.write(json.dumps(response).encode('utf-8'))


def generate_chart(server_data):
    for a in server_data.accumulator:
        server_data.nodes.add(a[1])

    _, axes = plt.subplots()

    for node in server_data.nodes:
        # Filter the events based on the value
        filtered_events = [event for event in server_data.accumulator if event[1] == node]

        # Extract the datetimes and data points for the filtered events
        datetimes = [datetime.fromtimestamp(event[0]) for
                     event in filtered_events]
        data_points = [event[2] for event in filtered_events]

        # Plot the line for the current value
        axes.plot(datetimes, data_points, label=f'Node: {node}')

    axes.xaxis.set_major_locator(mdates.AutoDateLocator())
    axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    plt.xlabel('Time')
    plt.title('Events Timeseries Chart')
    plt.xticks([])  # Hide the x-axis labels

    plt.tight_layout()

    output_dir = 'output'
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    full_path = f'{output_dir}/timeseries.png'
    plt.savefig(full_path)
    return full_path


def run_central_server(server_class=HTTPServer,
                       handler_class=DefaultCentralRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    def threaded_handler(income_signal, frame):
        print(f'Received signal {income_signal} and frame {frame}')

        def signal_handler():
            print('Termination signal received. Performing cleanup...')

            # Add your cleanup code or additional tasks here
            generate_chart(handler_class.mem)
            print('Generated summary chart.')
            # Shutdown the server
            httpd.shutdown()
            print('Shutdown successful.')
            httpd.server_close()
            print('Server gracefully shut down.')

        signal_thread = threading.Thread(target=signal_handler, args=())
        signal_thread.start()
        sys.exit(0)

    signal.signal(signal.SIGINT, threaded_handler)
    signal.signal(signal.SIGTERM, threaded_handler)
    print(f'Starting HTTP listener on port {port}...')
    httpd.serve_forever()
