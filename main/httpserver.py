from webclient import sendRequest

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import threading
import argparse
import re
import cgi
import json
from webclient import sendRequest
from computingserver import calculateSum


class LocalData(object):
    records = {}


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if None != re.search('/api/v1/addrecord/*', self.path):
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'application/json':
                content_len = int(self.headers.getheader('content-length', 0))
                post_body = self.rfile.read(content_len)
                print post_body
                j_data = json.loads(post_body)
                print j_data
                record = self.path.split('/')[-1].split('=')
                if len(record) == 2:
                    response = sendRequest('set', record[0], record[1])
                    if response is not None:
                        print "pair {0}, {1} is added successfully".format(record[0], record[1])
                    else:
                        self.sendError()
                else:
                    self.sendError()
            self.send_response(300)
            self.end_headers()
        else:
            self.sendError()
        return

    def sendError(self):
        self.send_response(403)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_GET(self):
        if None != re.search('/api/v1/getrecord/*', self.path):
            recordID = self.path.split('/')[-1]
            print recordID
            record = sendRequest('get', recordID)
            print record
            if record is not None:
                self.send_response(200)
                self.send_header('Content-Type', 'text')
                self.end_headers()
                self.wfile.write(record)
            else:
                self.send_response(400, 'Bad Request: record does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(
                    '{ "errors": [{"status": "400","detail": "record does not exist" }]}')
        elif re.search('/api/v1/sumrecords/*', self.path) is not None:
            keys = self.path.split('/')[-1].split('&')
            values = list()
            for key in keys:
                values.append(sendRequest('get', key))
            print values
            result = calculateSum(values)
            if result is not None:
                self.send_response(200)
                self.send_header('Content-Type', 'text')
                self.end_headers()
                self.wfile.write('The result of {0} is {1}\n'.format(values, result))
            else:
                self.send_response(400, 'Bad Request: record does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(
                    '{ "errors": [{"status": "400","detail": "wrong values" }]}')
        else:
            self.sendError()
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)


class SimpleHttpServer():
    def __init__(self, ip, port):
        self.server = ThreadedHTTPServer((ip, port), HTTPRequestHandler)

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def waitForThread(self):
        self.server_thread.join()

    def addRecord(self, recordID, jsonEncodedRecord):
        LocalData.records[recordID] = jsonEncodedRecord

    def stop(self):
        self.server.shutdown()
        self.waitForThread()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP Server')
    parser.add_argument('port', type=int, help='Listening port for HTTP Server')
    parser.add_argument('ip', help='HTTP Server IP')
    args = parser.parse_args()

    server = SimpleHttpServer(args.ip, args.port)
    print 'HTTP Server Running...........'
    server.start()
    server.waitForThread()
