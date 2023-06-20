#!/usr/bin/env python3

import json
import os
import random
import requests
import signal
import string
import sys
import threading
import time

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


class ServerInfo:
    accumulator = []
    nodes = set()


def random_word(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def random_number(top):
    return random.randint(1, top)


def generate_html(server_data):
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


def generate_chart(server_data):
    for a in server_data.accumulator:
        server_data.nodes.add(a[1])

    fig, ax = plt.subplots()

    for node in server_data.nodes:
        # Filter the events based on the value
        filtered_events = [event for event in server_data.accumulator if event[1] == node]

        # Extract the datetimes and data points for the filtered events
        datetimes = [datetime.fromtimestamp(event[0]) for
                     event in filtered_events]
        data_points = [event[2] for event in filtered_events]

        # Plot the line for the current value
        ax.plot(datetimes, data_points, label=f'Node: {node}')

    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    plt.xlabel('Time')
    plt.title('Events Timeseries Chart')
    plt.xticks([])  # Hide the x-axis labels

    plt.tight_layout()
    plt.savefig('timeseries.png')


class CentralHTTPRequestHandler(BaseHTTPRequestHandler):
    mem = ServerInfo()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = generate_html(self.mem)
        self.wfile.write(bytearray(html, encoding='utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        json_data = json.loads(post_data)

        self.send_response(204)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        thing_from = [
            json_data['when'],
            json_data['who'],
            json_data['how-much']
        ]
        self.mem.accumulator.append(thing_from)
        for a in self.mem.accumulator:
            self.mem.nodes.add(f'{a[1]} ({a[2]})')
        print(len(self.mem.accumulator))

        response = {'message': 'Received POST data successfully',
                    'data': json_data}
        self.wfile.write(json.dumps(response).encode('utf-8'))


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


def run_central_server(server_class=HTTPServer,
                       handler_class=CentralHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    def threaded_handler(sg, frame):
        print(f'Received signal {sg} and frame {frame}')

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


def main():
    mode = os.getenv("MODE")
    print("mode -> " + mode)

    if mode == "central":
        run_central_server()
    else:
        url = "http://" + os.getenv("SERVER")
        id = random_word(5)
        number = random_number(100)
        while True:
            data = {
                "when": datetime.now().timestamp(),
                "who": id,
                "how-much": number
            }
            send_post_request(url, data)
            time.sleep(1)


if __name__ == "__main__":
    main()
