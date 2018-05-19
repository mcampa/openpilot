import sys
import json
import zmq

sys.path.append("/data/deps")
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5555")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pid-save', methods=['POST'])
def pid_save():
    p = request.form.get('p')
    i = request.form.get('i')
    d = request.form.get('d')

    # TODO: validation

    socket.send(json.dumps({
        'p': p,
        'i': i,
        'd': d,
    }))

    message = socket.recv()
    return message

@socketio.on('my event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']})

@socketio.on('my broadcast event', namespace='/test')
def test_message_broadcast(message):
    emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

def start():
    socketio.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    start()
