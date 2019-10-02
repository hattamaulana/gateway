#!/usr/bin/python3
# Import semua package yang dibutuhkan
from firebase import firebase
import serial


# ID ini merupakan ID dari setiap board
ID = 'kopinema-123'

# Berikut merupakan PORT & RATE untuk berkomunikasi
# dengan arduino
PORT = '/dev/ttyACM0'
RATE = 9600

"""
    Berikut Merupakan target REFERENCE
    yang digunakan pada firebase realtime database.
"""
BOARD_REF = '/database/board'
QUEUE_REF = '/database/queue'

# Setup Koneksi ke Arduino UNO R3
_serial = serial.Serial(PORT, RATE)
_serial.flushInput()

_db = firebase.FirebaseApplication(
    'https://kopinema-cc4c2.firebaseio.com/', None)
_on_process = False
_queue = {}
_board = id_board()

def id_board():
    """
        Method ini digunakan untuk mengambil data
        untuk mengetahui informasi tentang board.
        Lalu menguji apakah idboard sudah didaftarkan
        atau belum.

        @return string
    """
    snapshot = _db.get(BOARD_REF, None)

    for id in snapshot:
        if snapshot[id]['id'] == ID:
            snapshot[id]['bid'] = id
            return snapshot[id]


def update_status(id, status):
    """
        Method ini digunakan untuk mengupdate
        data board. Tepatnya pada data onProcess.
    """
    data = {'id': ID, 'active': True, 'onProcess': status}
    target = BOARD_REF + '/' + id

    _db.patch(target, data)


def get_queue():
    """
        Method ini digunakan untuk mengambil
        semua data yang masuk dalam antrian.
        Jika terdapat data lalu di sorting
        berdasarkan data waktu. Data paling
        atas akan di return.

        @return []
    """
    res = []
    snapshot = _db.get(QUEUE_REF, None)

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
    """ 
        Method ini digunakan untuk
        menghapus data pada antrian.
    """
    _db.delete(QUEUE_REF, id)

# Update status board menjadi siap digunakan.
update_status(_board['bid'], True)

# Main Program.
while True:
    """
        Pada Main program akan menguji, Apakah
        tidak ada proses yang dijalankan ?.
        Jika tidak ada proses dan program menerima
        data dari arduino uno maka mengaktifkan 
        program sehingga status prosesnya adalah true
        atau terdapat proses. Jika proses telah selesai
        program akan mengupdate data yang ada dalam database.
    """
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
