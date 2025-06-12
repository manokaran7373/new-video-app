from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active rooms and their participants
rooms = {}
# Store user connections
user_connections = {}

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/create-meeting')
def create_meeting():
    meeting_id = str(uuid.uuid4())
    rooms[meeting_id] = []
    return {'meeting_id': meeting_id}

@app.route('/join/<meeting_id>')
def join_meeting(meeting_id):
    return render_template('meeting.html', meeting_id=meeting_id)

@socketio.on('connect')
def handle_connect():
    user_connections[request.sid] = None

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    
    join_room(room)
    user_connections[request.sid] = {'room': room, 'username': username}
    
    if room not in rooms:
        rooms[room] = []
    
    # Add new user to room
    rooms[room].append({
        'username': username,
        'sid': request.sid
    })
    
    # Notify everyone in the room about the new user
    emit('user_joined', {
        'username': username,
        'users': rooms[room]
    }, room=room)
    
    # Send existing peers to the new user
    emit('existing_peers', {
        'users': rooms[room],
        'current_user': username
    }, room=request.sid)

@socketio.on('start_call')
def start_call(data):
    room = data['room']
    target_sid = data['target_sid']
    emit('call_user', {
        'offer': data['offer'],
        'caller': request.sid
    }, room=target_sid)

@socketio.on('accept_call')
def accept_call(data):
    caller_sid = data['caller']
    emit('call_accepted', {
        'answer': data['answer'],
        'acceptor': request.sid
    }, room=caller_sid)

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    target_sid = data['target_sid']
    emit('ice_candidate', {
        'candidate': data['candidate'],
        'sender': request.sid
    }, room=target_sid)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    
    if room in rooms:
        rooms[room] = [user for user in rooms[room] if user['sid'] != request.sid]
        leave_room(room)
        
        emit('user_left', {
            'username': username,
            'sid': request.sid,
            'users': rooms[room]
        }, room=room)
        
        if len(rooms[room]) == 0:
            del rooms[room]

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in user_connections:
        user_data = user_connections[request.sid]
        if user_data:
            room = user_data['room']
            username = user_data['username']
            if room in rooms:
                rooms[room] = [user for user in rooms[room] if user['sid'] != request.sid]
                emit('user_left', {
                    'username': username,
                    'sid': request.sid,
                    'users': rooms[room]
                }, room=room)
                
                if len(rooms[room]) == 0:
                    del rooms[room]
        
        del user_connections[request.sid]

@socketio.on('chat_message')
def handle_message(data):
    room = data['room']
    emit('chat_message', {
        'username': data['username'],
        'message': data['message']
    }, room=room)

if __name__ == '__main__':
<<<<<<< HEAD
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
=======
    socketio.run(app, host='0.0.0.0', port=5000, debug=True,allow_unsafe_werkzeug=True)
>>>>>>> d3378ebcf990e7d15539a60250095b135a01239f
