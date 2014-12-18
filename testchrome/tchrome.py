import re
import time
import json
import bottle

from collections import defaultdict
from bottle import route, run, request, response, view, redirect, static_file, template

@route('/app')
def serve_main():
    return static_file('tchrome.html', root='')


@route('/doc/:number')
def serve_document(number):
    #print dir (request)
    print "Serving document "+number+" as "+request.headers.get('Accept')
    #if request.header.get('X-Requested-With') == 'XMLHttpRequest':
    if 'application/json' in request.headers.get('Accept'):
        response.set_header('Content-Type','application/json')
        return json.dumps({'msg':'User is offline'})
    else:
        return static_file("001_"+number+".png", root='', mimetype='image/png')

@route('/:filename')
def serve_image(filename):
    print "Serving static "+filename+" as "+request.headers.get('Accept')
    return static_file(filename, root='', mimetype='image/png')


if __name__=='__main__':
    import socket
    ipaddr = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][0]
    run(host=ipaddr, port=8080)
