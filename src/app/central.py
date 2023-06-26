"""
Central server functions
"""

import json
import os
import signal
import sys
import threading

from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

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
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = self.generate_html(self.mem)
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

        response = {'message': 'Received POST data successfully',
                    'data': json_data}
        self.wfile.write(json.dumps(response).encode('utf-8'))


def run_central_server(server_class=HTTPServer,
                       handler_class=DefaultCentralRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

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
        os.mkdir("output")
        plt.savefig('output/timeseries.png')

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