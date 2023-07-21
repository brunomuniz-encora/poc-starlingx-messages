import os
from http.server import BaseHTTPRequestHandler
from http import HTTPStatus

class RequestHandler(BaseHTTPRequestHandler):
    image_name = ''

    def do_GET(self):
        if os.path.isfile('.' + self.path) and self.path.endswith('png'):
            with open('.' + self.path, 'rb') as file:
                content = file.read()

            self.send_response_only(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()

            self.wfile.write(content)
        elif self.path == '/':
            self.send_response_only(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            #print(f'Sending HTML page to {self.client_address[0]}:{self.client_address[1]}')

            html =   '<!DOCTYPE html>\n'
            html +=  '<html>\n'
            html +=  '   <head>\n'
            html +=  '       <title>Dashboard</title>\n'
            html +=  '       <meta http-equiv="refresh" content="1">\n'
            html +=  '   </head>\n'
            html +=  '   <body>\n'
            html +=  '       <h2>Threats percentage</h2>\n'
            html += f'       <img src="{self.image_name}.png">\n'
            html +=  '   </body>\n'
            html +=  '</html>\n'

            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        self.send_error(HTTPStatus.NOT_IMPLEMENTED, 'POST not implemented')
