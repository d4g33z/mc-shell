import ast
import threading
from threading import Thread, Event
from io import StringIO

from flask import Flask, current_app,request, jsonify, send_from_directory, session
from flask_socketio import SocketIO
from flask import Flask, render_template_string, make_response



from mcshell.mcactions import MCActions
from mcshell.mcplayer import MCPlayer
from mcshell.constants import *
from mcshell.mcrepo import JsonFileRepository

from .blueprints.powers_api import powers_bp
from .blueprints.ipython_api import ipython_bp
from .blueprints.control_api import control_bp

class ServerShutdownException(Exception):
    """Custom exception to signal a clean server shutdown."""
    pass

# --- Server Setup ---
app = Flask(__name__, static_folder=str(MC_APP_DIR)) # Serve files from Parcel's build output
socketio = SocketIO(app, cors_allowed_origins="*", async_handlers=False, async_mode='threading')

app.register_blueprint(powers_bp)
app.register_blueprint(control_bp)
app.register_blueprint(ipython_bp)

app.secret_key = str(uuid.uuid4())

import logging
# --- Suppress Flask's Default Console Logging ---
flask_logger = logging.getLogger('werkzeug') # Get Werkzeug logger (Flask's dev server)
#flask_logger.setLevel(logging.ERROR) # Set Werkzeug logger level to ERROR or WARNING (or higher)
flask_logger.setLevel(logging.DEBUG) # Set Werkzeug logger level to ERROR or WARNING (or higher)
# Alternatively, to completely remove the default Werkzeug console handler:
# flask_logger.handlers = [] # Remove all handlers, including console

# --- State Management for Running Powers ---
# This dictionary will hold the state of each running power
# Key: power_id (a UUID string)
# Value: {'thread': ThreadObject, 'cancel_event': EventObject}
RUNNING_POWERS = {}

@app.route('/api/execute_power', methods=['POST'])
def execute_power():
    """Executes a saved power with runtime parameters from the control UI."""
    data = request.get_json() if request.is_json else request.form
    power_id = data.get('power_id')
    runtime_params = {k: v for k, v in data.items() if k != 'power_id'}

    player_name = current_app.config.get('MINECRAFT_PLAYER_NAME')
    server_data = current_app.config.get('MCSHELL_SERVER_DATA')
    power_repo = current_app.config.get('POWER_REPO')

    if not all([power_id, player_name, server_data, power_repo]):
        return "Error: Server or player not configured", 500

    power_data = power_repo.get_full_power(power_id)
    if not power_data or not power_data.get("python_code"):
        return jsonify({"error": "Power or its code not found."}), 404

    python_code = power_data["python_code"]

    # --- Create a unique ID for this execution instance ---
    execution_id = str(uuid.uuid4())
    cancel_event = Event()

    thread = Thread(target=execute_power_in_thread, args=(
        execution_id, python_code, player_name, server_data, runtime_params, cancel_event
    ))
    thread.daemon = True
    thread.start()

    RUNNING_POWERS[execution_id] = {'thread': thread, 'cancel_event': cancel_event}

    # ... (return the HTML with the cancel button containing the execution_id) ...
def execute_power_in_thread(execution_id, python_code, player_name, server_data, runtime_params, cancel_event):
    """
    This is the new, shared worker function. It runs in a background thread.
    """
    print(f"THREAD {execution_id}: Started for player '{player_name}' with params: {runtime_params}")
    socketio.emit('power_status', {'id': execution_id, 'status': 'running'})

    try:
        # We need the app context for config
        with app.app_context():
            mc_player = MCPlayer(player_name, **server_data)
            action_implementer = MCActions(mc_player)

            execution_scope = {
                # 'np': np, 'math': math, 'Vec3': Vec3, 'Matrix3': Matrix3
            }
            exec(python_code, execution_scope)

            BlocklyProgramRunner = execution_scope.get('BlocklyProgramRunner')
            if not BlocklyProgramRunner:
                raise RuntimeError("BlocklyProgramRunner class not found in generated code.")

            runner = BlocklyProgramRunner(action_implementer, cancel_event=cancel_event,**runtime_params)

            # --- Cancellation Check (if your MCActions methods support it) ---
            # You could pass the cancel_event to the runner if methods can check it.
            # runner.cancel_event = cancel_event

            runner.run_program()

            if cancel_event.is_set():
                print(f"Thread {execution_id}: Execution was cancelled.")
                socketio.emit('power_status', {'id': execution_id, 'status': 'cancelled'})
                return

        print(f"Thread {execution_id}: Execution completed successfully.")
        socketio.emit('power_status', {'id': execution_id, 'status': 'finished'})
    except Exception as e:
        # Report any errors that occur during execution
        print(f"Thread {execution_id}: Error during execution: {e}")
        import traceback
        traceback.print_exc()
        socketio.emit('power_status', {'id': execution_id, 'status': 'error', 'message': str(e)})
    finally:
        # Clean up the power from our tracking dictionary
        if execution_id in RUNNING_POWERS:
            del RUNNING_POWERS[execution_id]

# ... (other code) ...
# @app.route('/api/execute_power', methods=['POST'])
# def execute_power():
#     """
#     Executes a saved power by its ID with runtime parameters from the control UI.
#     This endpoint receives a power_id and a dictionary of parameters, then
#     spawns a background thread to run the power's logic.
#     """
#     if request.is_json:
#         data = request.get_json()
#     else:
#         data = request.form.to_dict()
#
#     power_id = data.get('power_id')
#     runtime_params = {k: v for k, v in data.items() if k != 'power_id'}
#
#     player_name = current_app.config.get('MINECRAFT_PLAYER_NAME')
#     server_data = current_app.config.get('MCSHELL_SERVER_DATA')
#     power_repo = current_app.config.get('POWER_REPO')
#
#     if not all([power_id, player_name, server_data, power_repo]):
#         return jsonify({"error": "Server or player not configured, or missing power_id."}), 500
#
#     # Create a unique ID for this specific execution instance
#     execution_id = str(uuid.uuid4())
#     cancel_event = Event()
#
#     # Create and start the thread
#     thread = Thread(target=execute_power_thread, args=(
#         execution_id,
#         power_id,
#         player_name,
#         server_data,
#         runtime_params,
#         cancel_event
#     ))
#     thread.daemon = True
#     thread.start()
#
#     # Store the thread and its cancellation event using the unique execution_id
#     RUNNING_POWERS[execution_id] = {'thread': thread, 'cancel_event': cancel_event}
#
#     print(f"Dispatched execution {execution_id} for power {power_id} with params {runtime_params}")
#
#     # Return the initial status update, including a "Cancel" button with the unique execution_id
#     cancel_button_html = f"""
#     <button class="btn-small btn-danger"
#             hx-post="/api/cancel_power"
#             hx-vals='{{"execution_id": "{execution_id}"}}'
#             hx-target="closest .power-widget .power-status"
#             hx-swap="innerHTML">
#         Cancel
#     </button>
#     """
#     return f'<span style="color: orange;">Executing...</span>{cancel_button_html}'

# def execute_power_thread(execution_id, power_id, player_name, server_data, runtime_params, cancel_event):
#     """
#     This function runs in a separate thread. It loads the generated Python code
#     for a power, instantiates all necessary classes, and executes the power's
#     run_program() method with the provided runtime parameters.
#     """
#     print(f"Thread {execution_id}: Started for power '{power_id}' with params: {runtime_params}")
#
#     # Use socketio.emit for real-time status updates to the client
#     socketio.emit('power_status', {
#         'id': power_id, # The power's ID for the widget
#         'execution_id': execution_id,
#         'status': 'running'
#     })
#
#     try:
#         # We need access to the app context to get the repository
#         with app.app_context():
#             power_repo = current_app.config.get('POWER_REPO')
#
#             # 1. Load the full power data, including the python_code
#             power_data = power_repo.get_full_power(power_id)
#             if not power_data:
#                 raise ValueError(f"Power with ID {power_id} not found in repository.")
#
#             python_code = power_data.get("python_code")
#             if not python_code:
#                 raise ValueError(f"Power {power_id} has no Python code to execute.")
#
#             # 2. Set up the execution environment
#             mc_player = MCPlayer(player_name, **server_data)
#             action_implementer = MCActions(mc_player)
#
#             # 3. Use exec() to define the BlocklyProgramRunner class in a temporary scope
#             execution_scope = {
#                 # Provide necessary classes/modules to the exec scope
#                 # 'np': np,
#                 # 'math': math,
#                 # 'Vec3': Vec3,
#                 # 'Matrix3': Matrix3
#             }
#             exec(python_code, execution_scope)
#
#             BlocklyProgramRunner = execution_scope.get('BlocklyProgramRunner')
#             if not BlocklyProgramRunner:
#                 raise RuntimeError("Could not find BlocklyProgramRunner class in the provided code.")
#
#             # 4. Instantiate the runner, passing the action implementer AND the runtime params
#             runner = BlocklyProgramRunner(action_implementer, runtime_params)
#
#             # 5. Run the main program logic
#             runner.run_program()
#
#             # (Advanced) Your long-running loops inside MCActions could periodically check cancel_event.is_set()
#             if cancel_event.is_set():
#                 print(f"Thread {execution_id}: Execution was cancelled.")
#                 socketio.emit('power_status', {'id': power_id, 'status': 'cancelled'})
#                 return
#
#         print(f"Thread {execution_id}: Execution completed successfully.")
#         socketio.emit('power_status', {'id': power_id, 'status': 'finished'})
#
#     except Exception as e:
#         # Report any errors that occur during execution
#         print(f"Thread {execution_id}: Error during execution: {e}")
#         import traceback
#         traceback.print_exc()
#         socketio.emit('power_status', {'id': power_id, 'status': 'error', 'message': str(e)})
#     finally:
#         # Clean up the power from our tracking dictionary
#         if execution_id in RUNNING_POWERS:
#             del RUNNING_POWERS[execution_id]

@app.route('/api/cancel_power', methods=['POST'])
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
    return send_from_directory(current_app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Serve any other static files (JS, CSS) from the 'dist' directory
    return send_from_directory(current_app.static_folder, path)




# -- Server Control ---
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

def start_app_server(server_data,mc_name,ipy_shell):
    """Starts the main Flask-SocketIO application server in a separate thread."""
    # Attach the server_data dict to the Flask app's config object.
    # This makes the data available anywhere we have access to the app context.
    # --- Inject the AUTHORITATIVE data into the Flask app config ---
    # The Flask server will now start with the correct, non-spoofable identity.
    app.config['MCSHELL_SERVER_DATA'] = server_data
    app.config['MINECRAFT_PLAYER_NAME'] = mc_name
    app.config['IPYTHON_SHELL'] = ipy_shell # <--- ADD THIS LINE

    # --- Instantiate the chosen repository ---
    # You can later make this configurable (e.g., via an environment variable)
    # to switch between JsonFileRepository, SqliteRepository, etc.
    power_repo = JsonFileRepository(mc_name)

    app.config['POWER_REPO'] = power_repo


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