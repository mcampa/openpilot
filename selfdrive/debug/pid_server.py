import time
import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://127.0.0.1:5555")

def get_message():
    message = None
    try:
        message = socket.recv(zmq.NOBLOCK)
        socket.send(b"OK")
    except zmq.error.Again:
      pass
    return message


def update(LaC=None):
    new_pid_values = get_message()
    if new_pid_values:
        values = json.loads(new_pid_values)
        p = float(values.get('p', '0'))
        i = float(values.get('i', '0'))
        d = float(values.get('d', '0'))

        if (LaC):
            LaC.pid.set_pid(
                ([0.], [p]),
                ([0.], [i]),
                ([0.], [d])
            )
        else:
            print p, i, d


if __name__ == '__main__':
    while True:
        update()
        time.sleep(1)
