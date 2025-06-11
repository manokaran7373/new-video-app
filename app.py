from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

rooms = {}

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/create-meeting')
def create_meeting():
    meeting_id = str(uuid.uuid4())
    return {'meeting_id': meeting_id}

@app.route('/join/<meeting_id>')
def join_meeting(meeting_id):
    return render_template('meeting.html', meeting_id=meeting_id)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    if room not in rooms:
        rooms[room] = []
    rooms[room].append({'username': username, 'sid': request.sid})
    emit('user_joined', {'username': username, 'users': rooms[room]}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    rooms[room] = [user for user in rooms[room] if user['sid'] != request.sid]
    emit('user_left', {'username': username, 'users': rooms[room]}, room=room)

# Add this new route handler in your existing app.py
@socketio.on('chat_message')
def handle_message(data):
    room = data['room']
    emit('chat_message', {
        'username': data['username'],
        'message': data['message']
    }, room=room)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
