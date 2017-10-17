from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import redis


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


# Create server
server = SimpleXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler, allow_none=True)
# Redis connection
r = redis.StrictRedis(host='localhost', port=6379, db=0)


def get(key):
    return r.get(key)


def set(key, value):
    return r.set(key, value)


server.register_function(get)
server.register_function(set)

# Run the server's main loop
server.serve_forever()
