import threading
from threading import Thread, Event

from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit


from mcshell.mcactions import MCActions
from mcshell.mcplayer import MCPlayer
from mcshell.constants import *

class ServerShutdownException(Exception):
    """Custom exception to signal a clean server shutdown."""
    pass

# --- Server Setup ---
app = Flask(__name__, static_folder=str(MC_APP_DIR)) # Serve files from Parcel's build output
socketio = SocketIO(app, cors_allowed_origins="*", async_handlers=False, async_mode='threading')

# --- State Management for Running Powers ---
# This dictionary will hold the state of each running power
# Key: power_id (a UUID string)
# Value: {'thread': ThreadObject, 'cancel_event': EventObject}
RUNNING_POWERS = {}

# --- Helper function that will be the target of our thread ---
def execute_power_thread(code_to_execute, player_name, power_id, cancel_event,server_data):
    """
    This function runs in a separate thread. It instantiates the necessary
    classes and executes the generated Blockly code.
    """
    print(f"[{power_id}] Thread started for player {player_name}.")
    socketio.emit('power_status', {'id': power_id, 'status': 'running'})

    try:
        # 1. Instantiate the player and action classes for this thread
        # In a real app, you'd have a way to manage player connections/authentication
        mc_player = MCPlayer(player_name,**server_data)
        action_implementer = MCActions(mc_player) # Your class with create_cube etc.

        # 2. Prepare the execution scope
        # The generated code expects 'BlocklyProgramRunner' and its dependencies
        # to be available. We execute the entire generated script to define the class.
        execution_scope = {}
        exec(code_to_execute, execution_scope)

        # 3. Instantiate and run the generated program
        BlocklyProgramRunner = execution_scope.get('BlocklyProgramRunner')
        if BlocklyProgramRunner:
            runner = BlocklyProgramRunner(action_implementer)
            runner.run_program() # This is where the main blockly code runs

            # Check for cancellation periodically within long-running Python loops if possible
            # (This is an advanced feature for your geometry functions)
            if cancel_event.is_set():
                print(f"[{power_id}] Execution cancelled during run.")
                socketio.emit('power_status', {'id': power_id, 'status': 'cancelled'})
                return

            print(f"[{power_id}] Execution completed successfully.")
            socketio.emit('power_status', {'id': power_id, 'status': 'finished'})
        else:
            raise RuntimeError("BlocklyProgramRunner class not found in generated code.")

    except Exception as e:
        print(f"[{power_id}] Error during execution: {e}")
        socketio.emit('power_status', {'id': power_id, 'status': 'error', 'message': str(e)})
    finally:
        # Clean up the power from our tracking dictionary
        if power_id in RUNNING_POWERS:
            del RUNNING_POWERS[power_id]


# --- API Endpoints ---

@app.route('/execute_power', methods=['POST'])
def execute_power():
    data = request.get_json()
    python_code = data.get('code')
    player_name = data.get('playerName') # Get player name from request

    # --- Get the server data from the app's config ---
    server_data_for_thread = app.config.get('MCSHELL_SERVER_DATA')
    if not python_code:
        return jsonify({"error": "No code provided"}), 400

    power_id = str(uuid.uuid4())
    cancel_event = Event()

    # Create and start the thread
    thread = Thread(target=execute_power_thread, args=(python_code, player_name, power_id, cancel_event,server_data_for_thread))
    thread.daemon = True # Allows main program to exit even if threads are running
    thread.start()

    # Store the thread and its cancellation event
    RUNNING_POWERS[power_id] = {'thread': thread, 'cancel_event': cancel_event}

    print(f"Dispatched power {power_id} for execution.")
    return jsonify({"status": "dispatched", "power_id": power_id})


@app.route('/cancel_power', methods=['POST'])
def cancel_power():
    data = request.get_json()
    power_id = data.get('power_id')

    if power_id and power_id in RUNNING_POWERS:
        print(f"Received cancellation request for power {power_id}.")
        RUNNING_POWERS[power_id]['cancel_event'].set() # Set the event flag
        return jsonify({"status": "cancellation_requested"})
    else:
        return jsonify({"error": "Invalid or unknown power_id"}), 404

# --- Static File Serving ---

@app.route('/')
def serve_index():
    # Serve index.html from the 'dist' directory created by 'parcel build'
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Serve any other static files (JS, CSS) from the 'dist' directory
    return send_from_directory(app.static_folder, path)

app_server_thread = None

# --- NEW SOCKET.IO SHUTDOWN HANDLER ---
@socketio.on('shutdown_request')
def handle_shutdown_request():
    """
    Handles a shutdown request received over a Socket.IO event.
    This is the clean way to stop the socketio.run() loop.
    """
    print("Shutdown request received via Socket.IO. Stopping server.")
    socketio.stop() # This gracefully exits the socketio.run() loop.


# --- CORRECTED Thread Management Functions ---

def start_app_server(server_data):
    """Starts the main Flask-SocketIO application server in a separate thread."""
    # Attach the server_data dict to the Flask app's config object.
    # This makes the data available anywhere we have access to the app context.

    app.config['MCSHELL_SERVER_DATA'] = server_data

    global app_server_thread
    if app_server_thread and app_server_thread.is_alive():
        print("Application server is already running.")
        return

    # The target no longer needs a try/except block because socketio.stop()
    # provides a clean exit from the run() loop.
    app_server_thread = threading.Thread(
        target=lambda: socketio.run(app, host='0.0.0.0', port=5001, debug=True, use_reloader=False, allow_unsafe_werkzeug=False),
        daemon=True
    )
    app_server_thread.start()
    time.sleep(1) # Give the server a moment to start
    if app_server_thread.is_alive():
        print(f"Flask-SocketIO application server started in thread: {app_server_thread.ident}")
    else:
        print("Error: Application server thread failed to start.")


def stop_app_server():
    """Gracefully stops the Flask-SocketIO application server by emitting a socket.io event."""
    global app_server_thread
    if not app_server_thread or not app_server_thread.is_alive():
        print("Application server is not running.")
        return

    # Import the client library only when needed
    import socketio as socketio_client

    print("Connecting to server to send shutdown event...")
    sio = socketio_client.Client()
    try:
        sio.connect('http://127.0.0.1:5001')
        print("Connected. Emitting shutdown_request event.")
        sio.emit('shutdown_request')
        sio.disconnect()
        print("Shutdown event sent and client disconnected.")
    except Exception as e:
        print(f"Could not connect to server to send shutdown event: {e}")
        print("The server might already be down or unresponsive.")

    # Now, wait for the thread to fully terminate. This will now succeed.
    print(f"This function is broken and deadlocked, exit IPython to kill the server")
    print(f"Hit Ctrl-C")
    app_server_thread.join()

    if app_server_thread.is_alive():
        print("Warning: Server thread did not shut down cleanly.")
    else:
        print("Application server thread has shut down successfully.")

    app_server_thread = None

if __name__ == '__main__':
    start_app_server()
    time.sleep(10)
    stop_app_server()