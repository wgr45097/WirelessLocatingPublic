
"""
License: MIT License
Copyright (c) 2023 Miel Donkers
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import logging
from db_interface import insert_to_signals_database
from time import sleep
from http import HTTPStatus


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\n",
            str(self.path), str(self.headers))
        if 'Expect' in self.headers and self.headers['Expect'] == '100-continue':
            #self.send_response_only(HTTPStatus.CONTINUE)
            self.send_response_only(100)
            self.end_headers()
            logging.info("Send 100 Continue")

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("%d, %d" % (content_length, len(post_data)))
        if len(post_data) == content_length:
            raw_data = post_data.decode('utf-8')
            logging.info("Body:\n%s\n",
                    raw_data)
            with open("output.json", "a") as f:
                f.write(raw_data + '\n')
            insert_to_signals_database(raw_data)
        else:
            logging.info("Error: Incomplete Content\n")

        self._set_response()

def run(server_class=ThreadingHTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class, False)
    httpd.request_queue_size = 4096
    try:
        httpd.server_bind()
        httpd.server_activate()
    except:
        httpd.server_close()
        raise
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
