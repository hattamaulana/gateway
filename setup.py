from firebase import firebase
import serial


ID = 'kopinema-123'
PORT = '/dev/ttyACM0'
RATE = 9600
BOARD_REF = '/database/board'
QUEUE_REF = '/database/queue'

_serial = serial.Serial(PORT, RATE)
_serial.flushInput()
_database = firebase.FirebaseApplication('https://kopinema-cc4c2.firebaseio.com/', None)


def id_board():
    snapshot = _database.get(BOARD_REF, None)

    for id in snapshot:
        if snapshot[id]['id'] == ID:
            snapshot[id]['bid'] = id
            return snapshot[id]


def update_status(id, status):
    data = {'id': ID, 'active': True, 'onProcess': status}
    target = BOARD_REF + '/' + id

    _database.patch(target, data)


def get_queue():
    res = []
    snapshot = _database.get(QUEUE_REF, None)

    if snapshot is not None:
        for i in snapshot:
            if snapshot[i]['id_board'] == ID:
                snapshot[i]['id'] = i
                res.append(snapshot[i])

        res = sorted(res, key=lambda key: key['time'])

        if len(res) > 0:
            return res[0]
        else:
            return res

    else:
        return res


def remove(id):
    _database.delete(QUEUE_REF, id)


_on_process = False
_queue = {}
_board = id_board()
update_status(_board['bid'], True)

while True:
    if not _on_process:
        _queue = get_queue()

        if len(_queue) > 0:
            data = _queue['rasio']['coffee']
            _serial.write(str(data))
            print(_queue)

            # Update Status Board
            _on_process = True
            update_status(_board['bid'], _on_process)

    else:
        if _serial.inWaiting() > 0:
            input = _serial.readline()

            if input.strip() == "done":
                remove(_queue['id'])
                _on_process = False
                update_status(_board['bid'], _on_process)
                print('End')
