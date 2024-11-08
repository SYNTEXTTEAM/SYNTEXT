import logging
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, send
from datetime import datetime
import random
import json

maxusername=20
app=Flask(__name__)
app.config['key']='SYNTAXERROR'
socketio=SocketIO(app)
timestamp= datetime.now().strftime('%H:%M:%S')

logging.basicConfig(
    filename='/home/joaquin/personal coding/chat/logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger=logging.getLogger(__name__)

@app.route('/')
def home():
    logger.info("Rendering html")
    return render_template('chat.html')

@app.route('/todo')
def todo():
    return render_template('todo.html')

@app.route('/submit-idea', methods=['POST'])
def submit_idea():
    data = request.json
    idea = data.get('idea', '')
    logger.info(f'New idea submitted: {idea}')
    try:
        with open('/home/joaquin/personal coding/chat/logs/submissions.txt', 'a') as file:
            file.write(f'{idea}\n')  
    except Exception as e:
        logger.error(f'Error saving idea: {e}')
        return jsonify({'error': 'Error saving idea. Please try again later.'}), 500
    return jsonify({'message': 'Idea submitted successfully!'}), 200

@app.route('/random-splash', methods=['GET'])
def randomsplash():
    with open('/home/joaquin/personal coding/chat/nowwith.txt', 'r') as file:
        splash = file.readlines()
    random_splash = random.choice(splash).strip()
    return jsonify({'quote': random_splash})

@app.route('/set-username', methods=['POST'])
def set_username():
    username=request.json.get('username', '')
    if len(username)>=maxusername:
        return jsonify({'error': f'Username cannot exceed {maxusername} characters.'}), 400
    return jsonify({'message': 'Username set successfully!'}), 200

@socketio.on('join')
def handle_join(data):
    username=data['username']
    room=data['room']
    join_room(room)
    message_data = {
        'username': 'Server',
        'message': f"{username} has entered {room}",
    }
    socketio.emit('message', message_data, room=room)
    
@socketio.on('leave')
def handle_leave(data):
    username=data['username']
    room=data['room']
    leave_room(room)
    message_data = {
        'username': 'Server',
        'message': f"{username} has left the room",
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    socketio.emit('message', message_data, room=room)

@socketio.on('message')
def handle_message(data):
    room=data.get('room')
    message=data.get('message')
    username=data.get('username')
    if not username:
        print("username is missing still")
        return
    message_data = {
        'username': username,
        'message': message,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    print(timestamp, "Received message data:", data)
    socketio.emit('message', message_data, room=room)
    
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=6969, debug=True)