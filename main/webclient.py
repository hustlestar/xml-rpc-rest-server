from httplib import HTTPConnection
import re


def prepareBody(method, *args):
    params = ''.join(['<param>\n<value><string>{0}</string></value>\n</param>'.format(x) for x in args])
    request_body = b"<?xml version='1.0'?>" \
                   b"\n<methodCall>\n<methodName>{0}</methodName>" \
                   b"\n<params>\n{1}\n</params>\n</methodCall>\n".format(method, params)
    return request_body


def parseResponse(response):
    value = '<value>'
    value = response[response.index(value) + len(value):response.index('</value>')]
    return value[value.index('>') + 1:value.index('</')]


def sendRequest(method, *args):
    print "request"
    connection = HTTPConnection('localhost:8000')
    connection.putrequest('POST', '/RPC2')
    connection.putheader('Content-Type', 'text/xml')
    connection.putheader('User-Agent', 'Python-xmlrpc/3.5')
    request_body = prepareBody(method, *args)
    print request_body
    connection.putheader("Content-Length", str(len(request_body)))
    connection.endheaders(request_body)

    print "response"
    response = connection.getresponse().read()
    print(response)
    return parseResponse(response)