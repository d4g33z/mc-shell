import ast
import threading
from threading import Thread, Event

from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask import Flask, render_template_string, make_response


from mcshell.mcactions import MCActions
from mcshell.mcplayer import MCPlayer
from mcshell.constants import *
from mcshell.mcrepo import JsonFileRepository

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
def execute_power_thread(code_to_execute, player_name, power_id, cancel_event, server_data):
    """
    This function now securely instantiates all objects before executing
    the received code.
    """
    print(f"[{power_id}] Thread started for player {player_name}.")
    socketio.emit('power_status', {'id': power_id, 'status': 'running'})
    try:
        # --- FIX: Convert server_data string to a dictionary ---
        parsed_server_data = {}
        if isinstance(server_data, str):
            try:
                # ast.literal_eval safely evaluates a string containing a Python literal
                parsed_server_data = ast.literal_eval(server_data)
                if not isinstance(parsed_server_data, dict):
                    raise TypeError("Parsed server_data is not a dictionary.")
            except (ValueError, SyntaxError, TypeError) as e:
                print(f"[{power_id}] CRITICAL ERROR: Could not parse server_data string: {e}")
                raise RuntimeError("Server data configuration is malformed.") from e
        elif isinstance(server_data, dict):
            # If it's already a dictionary, use it directly
            parsed_server_data = server_data
        else:
             raise TypeError(f"server_data must be a dict or a string representation of a dict, but got {type(server_data)}")

        # --- SERVER-SIDE IDENTITY ENFORCEMENT ---
        # 1. Instantiate the player using the AUTHORITATIVE player_name.
        #    The **server_data unpacks host, port, etc.
        mc_player = MCPlayer(player_name, **parsed_server_data)

        # 2. Instantiate the action implementer with the trusted player object.
        action_implementer = MCActions(mc_player)

        # 3. Prepare the execution scope and execute the received code string.
        #    This only DEFINES the BlocklyProgramRunner class in the scope.
        execution_scope = {}
        exec(code_to_execute, execution_scope)

        # 4. Get the class definition that was just created.
        BlocklyProgramRunner = execution_scope.get('BlocklyProgramRunner')

        if BlocklyProgramRunner:
            # 5. Instantiate the runner, passing our SECURELY created action_implementer.
            runner = BlocklyProgramRunner(action_implementer)

            # 6. Run the program. The logic from the blocks will now call methods
            #    on the secure action_implementer instance.
            runner.run_program()

            # ... (rest of the success/error/cancellation logic) ...
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

# @app.route('/execute_power', methods=['POST'])
# def execute_power():
#     data = request.get_json()
#     python_code = data.get('code')
#     player_name = data.get('playerName') # Get player name from request
#
#     # --- Get the server data from the app's config ---
#     server_data_for_thread = app.config.get('MCSHELL_SERVER_DATA')
#     print(server_data_for_thread)
#
#     if not python_code:
#         return jsonify({"error": "No code provided"}), 400
#
#     power_id = str(uuid.uuid4())
#     cancel_event = Event()
#
#     # Create and start the thread
#     thread = Thread(target=execute_power_thread, args=(python_code, player_name, power_id, cancel_event,server_data_for_thread))
#     thread.daemon = True # Allows main program to exit even if threads are running
#     thread.start()
#
#     # Store the thread and its cancellation event
#     RUNNING_POWERS[power_id] = {'thread': thread, 'cancel_event': cancel_event}
#
#     print(f"Dispatched power {power_id} for execution.")
#     return jsonify({"status": "dispatched", "power_id": power_id})
#

@app.route('/execute_power', methods=['POST'])
def execute_power():
    """
    Executes a saved power by its ID.
    The client no longer sends the code, only the ID of the power to run.
    """
    data = request.get_json()
    power_id = data.get('power_id')
    player_name = app.config.get('MINECRAFT_PLAYER_NAME')
    power_repo = app.config.get('POWER_LIBRARY')

    if not all([power_id, player_name]):
        return jsonify({"error": "Missing power_id or not authorized"}), 400

    # 1. Load the full power data, including the python_code
    full_power_data = power_repo.get_full_power(player_name, power_id)

    if not full_power_data:
        return jsonify({"error": "Power not found"}), 404

    python_code = full_power_data.get("python_code")

    # 2. The rest of the logic remains the same: start the thread with this code
    server_data = app.config.get('MCSHELL_SERVER_DATA')
    # ... create cancel_event, start thread ...
    # thread = Thread(target=execute_power_thread, args=(python_code, ...))
    # ...
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

@app.route('/api/powers', methods=['POST'])
def save_new_power():
    """Saves a new power from the editor."""
    player_id = app.config.get('MINECRAFT_PLAYER_NAME')
    power_repo = app.config.get('POWER_LIBRARY')
    if not player_id:
        return jsonify({"error": "No authorized player"}), 401

    power_data = request.get_json()
    if not power_data or "name" not in power_data:
        return jsonify({"error": "Invalid power data"}), 400

    power_id = power_repo.save_power(player_id, power_data)
    return jsonify({"success": True, "power_id": power_id}), 201



# --- This endpoint now returns HTML fragments, not JSON ---
@app.route('/api/powers', methods=['GET'])
def get_powers_list_as_html():
    """
    Fetches the list of saved powers and renders them as HTML widgets
    for the htmx-powered control panel.
    """
    player_id = app.config.get('MINECRAFT_PLAYER_NAME')
    power_repo = app.config.get('POWER_LIBRARY')
    if not player_id:
        # Return an empty response with an error header for htmx to potentially handle
        return make_response("", 204, {"HX-Trigger": "showError", "errorMessage": "No authorized player"})

    # 1. Fetch the summary data from the repository
    powers_summary_list = power_repo.list_powers(player_id)
    if not powers_summary_list:
        return "<p>No powers saved yet. Go to the editor to create one!</p>"

    # 2. Define the Jinja2 template for a single widget
    #    This template now uses the correct /execute_power endpoint and sends the power_id
    widget_template = """
    <div class="power-widget" id="{{ power.power_id }}">
        <div class="power-header">
            <span class="power-name">{{ power.name }}</span>
            <span class="power-category">{{ power.category }}</span>
        </div>
        <p class="power-description">{{ power.description }}</p>
        <div class="power-status">Status: Idle</div>
        <button class="execute-btn"
                hx-post="/execute_power"
                hx-vals='{"power_id": "{{ power.power_id }}"}'
                hx-target="#{{ power.power_id }} .power-status"
                hx-swap="innerHTML">
            Execute
        </button>
    </div>
    """

    # 3. Render a widget for each power and join them into a single HTML string
    html_response_string = "".join([render_template_string(widget_template, power=p) for p in powers_summary_list])

    # 4. Create a response object with caching disabled
    response = make_response(html_response_string)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

# You will also need a new endpoint for execution by name,
# which would load the code and then call the existing execute_power_thread.
@app.route('/execute_power_by_name', methods=['POST'])
def execute_power_by_name():
    power_repo = app.config.get('POWER_LIBRARY')
    power_name = request.form.get('power_name')
    print(f"Received request to execute power by name: {power_name}")

    # 1. Load the power's code from your repository
    # python_code = power_repo.load_power(player_id, power_name)
    # For now, just a placeholder:
    python_code = f"# This is the placeholder code for '{power_name}'"

    # 2. Reuse the existing threading logic to execute the code
    player_name = app.config.get('MINECRAFT_PLAYER_NAME')
    server_data = app.config.get('MCSHELL_SERVER_DATA')
    power_id = str(uuid.uuid4())
    cancel_event = Event()

    thread = Thread(target=execute_power_thread, args=(python_code, player_name, power_id, cancel_event, server_data))
    thread.daemon = True
    thread.start()

    RUNNING_POWERS[power_id] = {'thread': thread, 'cancel_event': cancel_event}

    # Return the initial status update for the widget
    return f'<span class="status" style="color: orange;">Running... (ID: {power_id[:4]})</span>'

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

def start_app_server(server_data,mc_name):
    """Starts the main Flask-SocketIO application server in a separate thread."""
    # Attach the server_data dict to the Flask app's config object.
    # This makes the data available anywhere we have access to the app context.
    # --- Inject the AUTHORITATIVE data into the Flask app config ---
    # The Flask server will now start with the correct, non-spoofable identity.
    app.config['MCSHELL_SERVER_DATA'] = server_data
    app.config['MINECRAFT_PLAYER_NAME'] = mc_name
    # --- Instantiate the chosen repository ---
    # You can later make this configurable (e.g., via an environment variable)
    # to switch between JsonFileRepository, SqliteRepository, etc.
    power_repo = JsonFileRepository(MC_POWER_LIBRARY_DIR.joinpath(f"{mc_name}.json"))
    app.config['POWER_LIBRARY'] = power_repo


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

# if __name__ == '__main__':
#     start_app_server()
#     time.sleep(10)
#     stop_app_server()