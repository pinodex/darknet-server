import sys, os
import json
import socketio
import eventlet
import eventlet.wsgi

from flask import Flask, request, render_template

sys.path.append(os.path.abspath('.'))

import darknet

base = os.path.abspath(__file__ + '/../../')

net = darknet.load_net(
    base + '/cfg/yolov3.cfg',
    base + '/weights/yolov3.weights', 0)

meta = darknet.load_meta(base + '/cfg/coco.data')

sio = socketio.Server()
app = Flask(__name__)

@sio.on('connect', namespace='/')
def connect(sid, environ):
    print("connect ", sid)

@sio.on('frame', namespace='/')
def message(sid, data):
    result = darknet.detect(net, meta, data)

    print result

    if result:
        output = json.dumps(result)
        sio.emit('result', output, room=sid)
        #print output

@sio.on('disconnect', namespace='/')
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)