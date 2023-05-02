import flask
from flask_socketio import SocketIO, emit

app = flask.Flask(__name__)
server = SocketIO(app, ping_timeout=3, ping_interval=2)
clients = []

@server.on('connect')
def connect_handler():
    print('connect from', flask.request.sid)
    headers = flask.request.headers
    print('headers:', headers)
    try:
        id = headers['id']
        clients.append(flask.request.sid)
        return True
    except KeyError:
        print('id not found in headers')
        return False

@server.on('disconnect')
def disconnect_handler():
    print('disconnect', flask.request.sid)
    try:
        clients.remove(flask.request.sid)
    except ValueError:
        print(f'{flask.request.sid} is not in clients list')

@server.on('test')
def test_handler(data):
    print('test_handler received:', data)
    emit('test', 'callClientTest')
    return 123

server.run(app,
           host='0.0.0.0',
           port=9192,
           debug=False,
           allow_unsafe_werkzeug=True)