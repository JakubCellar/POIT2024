import serial
import time
from threading import Lock
from flask import Flask, render_template, session, request, jsonify
from flask_socketio import SocketIO, emit, disconnect

# Inicializacia serioveho pripojenia
ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)

# Skontrolovanie ci je seriovy port otvoreny
if not ser.is_open:
    ser.open()

# Nastavenie Flask aplikacie
async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
write_data = False  # Premenna na kontrolu zapisovania dat

# Funkcia na citanie zo serioveho portu
def read_serial():
    try:
        income_message = ser.readline().decode("latin1").strip()
        if income_message.isdigit():
            return int(income_message)
        return None
    except serial.SerialException as e:
        print(f"Serial exception: {e}")
    return None

# Funkcia pre beziace vlakno na pozadi
def background_thread():
    global write_data
    while True:
        if write_data:
            data = read_serial()
            if data is not None:
                socketio.emit('my_response', {'data': data}, namespace='/test')
        socketio.sleep(1)

# Hlavna stranka aplikacie
@app.route('/')
def index():
    return render_template('tabs.html')

# Riesenie pripojenia klienta
@socketio.on('connect', namespace='/test')
def test_connect():
    global thread, write_data
    with thread_lock:
        if thread is None:
            write_data = True  # Povolenie zapisovania dat
            thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected'})
    ser.write(b'C')  # Posielanie písmena 'C' pri pripojení klienta

# Riesenie odpojenia klienta
@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    global thread, write_data
    write_data = False  # Zakázanie zapisovania dat
    print('Client disconnected')
    ser.write(b'O')  # Posielanie písmena 'O' pri odpojení klienta
    disconnect()
    
# Obsluha udalosti pre ovládanie LED diódy
@socketio.on('led_control', namespace='/test')
def handle_led_control(message):
    action = message.get('action')
    if action == 'toggle':
        ser.write(b'T')  # Posielanie písmena 'T' pre prepnutie stavu LED

# Obsluha udalosti pre odpojenie klienta
@socketio.on('disconnect_request', namespace='/test')
def handle_disconnect_request():
    disconnect()

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
