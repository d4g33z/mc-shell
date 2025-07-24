
import logging
import textwrap
import threading
from threading import Thread, Event

from flask import Flask, current_app,request, jsonify, send_from_directory
from flask_socketio import SocketIO


from mcshell.mcactions import MCActions
from mcshell.mcplayer import MCPlayer
from mcshell.constants import *
from mcshell.mcrepo import JsonFileRepository

from mcshell.blueprints.powers_api import powers_bp
from mcshell.blueprints.ipython_api import ipython_bp
from mcshell.blueprints.control_api import control_bp

class ServerShutdownException(Exception):
    """Custom exception to signal a clean server shutdown."""
    pass

# -- Server Control ---
app_server_thread = None

# --- Server Setup ---
app = Flask(__name__, static_folder=str(MC_APP_DIR)) # Serve files from Parcel's build output
app.secret_key = str(uuid.uuid4())

# --- Register Endpoints
app.register_blueprint(powers_bp)
app.register_blueprint(control_bp)
app.register_blueprint(ipython_bp)


# --- Suppress Flask's Default Console Logging ---
flask_logger = logging.getLogger('werkzeug') # Get Werkzeug logger (Flask's dev server)
flask_logger.setLevel(logging.DEBUG) # Set Werkzeug logger level to ERROR or WARNING (or higher)
# flask_logger.setLevel(logging.ERROR) # Set Werkzeug logger level to ERROR or WARNING (or higher)
# Alternatively, to completely remove the default Werkzeug console handler:
# flask_logger.handlers = [] # Remove all handlers, including console

socketio = SocketIO(
    app, cors_allowed_origins="*", async_handlers=True, async_mode='eventlet',engineio_logger=flask_logger,logger=flask_logger)

# --- State Management for Running Powers ---
# This dictionary will hold the state of each running power
# Key: power_id (a UUID string)
# Value: {'thread': ThreadObject, 'cancel_event': EventObject}
RUNNING_POWERS = {}

# --- Server Control ---
def start_app_server(server_data,mc_name,ipy_shell):
    """Starts the main Flask-SocketIO application server in a separate thread."""
    # Attach the server_data dict to the Flask app's config object.
    # This makes the data available anywhere we have access to the app context.
    # --- Inject the AUTHORITATIVE data into the Flask app config ---
    # The Flask server will now start with the correct, non-spoofable identity.
    app.config['MCSHELL_SERVER_DATA'] = server_data
    app.config['MINECRAFT_PLAYER_NAME'] = mc_name
    app.config['IPYTHON_SHELL'] = ipy_shell

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
        target=lambda: socketio.run(app, host='0.0.0.0', port=5001, debug=False, use_reloader=False, allow_unsafe_werkzeug=False),
        daemon=True
    )
    app_server_thread.start()
    time.sleep(1) # Give the server a moment to start
    if app_server_thread.is_alive():
        print(f"Flask-SocketIO application server started in thread: {app_server_thread.ident}")
        print(f"mc-ed application server started for player '{mc_name}'.")
    else:
        print("Error: Application server thread failed to start.")


def stop_app_server():
    """Gracefully stops the Flask-SocketIO application server by emitting a socket.io event."""
    global app_server_thread
    if not app_server_thread or not app_server_thread.is_alive():
        print("There is no application server running.")
        app_server_thread = None
        return

    # Import the client library only when needed
    import socketio as socketio_client
    sio = socketio_client.Client()
    try:
        print("CLient connecting to server to send shutdown event...")
        sio.connect('http://127.0.0.1:5001')
    except Exception as e:
        print(f"Could not connect to server to send shutdown event: {e}")
        print("The server might already be down or unresponsive.")
        return

    sio.emit('shutdown_request')
    app_server_thread = None


# --- Socket.io Shutdown Handler ---
@socketio.on('shutdown_request')
def handle_shutdown_request():
    """
    Handles a shutdown request received over a Socket.IO event.
    This is the clean way to stop the socketio.run() loop.
    """
    print("Shutdown request received via Socket.IO. Stopping server.")
    with app.app_context():
        socketio.stop() # This gracefully exits the socketio.run() loop.



# --- Helpers ---
def get_code_with_dependencies(power_repo, power_id_or_name, processed_names=None) -> dict:
    """
    Recursively loads a power and all of its dependencies by function name.
    Returns a dictionary of all unique method definitions required for execution.
    """
    if processed_names is None:
        processed_names = set()

    # The repository needs a way to find a power by its function name.
    # Let's assume you've added a find_power_by_function_name() method.
    power_data = power_repo.find_power_by_function_name(power_id_or_name)

    if not power_data:
        return {} # Base case for recursion

    func_name = power_data.get("function_name")
    if not func_name or func_name in processed_names:
        return {} # Already processed, break recursion

    processed_names.add(func_name)

    # Start with this power's own code
    all_method_definitions = {
        func_name: power_data.get("python_code")
    }

    # Recursively fetch code for all dependencies
    for dep_name in power_data.get("dependencies", []):
        dep_methods = get_code_with_dependencies(power_repo, dep_name, processed_names)
        all_method_definitions.update(dep_methods)

    return all_method_definitions

def execute_power_in_thread(power_id,execution_id, python_code, player_name, server_data, runtime_params, cancel_event):
    """
    This is the new, shared worker function. It runs in a background thread.
    """
    print(f"THREAD {execution_id}: Started for player '{player_name}' with params: {runtime_params}")
    # --- Send the initial 'running' status with ALL required fields ---
    socketio.emit('power_status', {
        'id': power_id,
        'execution_id': execution_id,
        'status': 'running',
        'message': ''
    })

    try:
        # We need the app context for config
        with app.app_context():
            mc_player = MCPlayer(player_name, **server_data,cancel_event=cancel_event)
            action_implementer = MCActions(mc_player)

            execution_scope = {
                # 'np': np, 'math': math, 'Vec3': Vec3, 'Matrix3': Matrix3
            }
            exec(python_code, execution_scope)

            BlocklyProgramRunner = execution_scope.get('BlocklyProgramRunner')
            if not BlocklyProgramRunner:
                raise RuntimeError("BlocklyProgramRunner class not found in generated code.")

            runner = BlocklyProgramRunner(action_implementer, cancel_event=cancel_event,runtime_params=runtime_params)

            # --- Cancellation Check (if your MCActions methods support it) ---
            try:
                runner.run_program()
            except PowerCancelledException:
                #we raise an exception only when polling for a sword strike
                pass
            if cancel_event.is_set():
                print(f"Thread {execution_id}: Execution was cancelled.")
                # --- Send the 'cancelled' status with ALL required fields ---
                socketio.emit('power_status', {
                    'id': power_id,
                    'execution_id': execution_id,
                    'status': 'cancelled',
                    'message': 'Cancelled by user.'
                })
                return

        print(f"Thread {execution_id}: Execution completed successfully.")
        # --- Send the 'finished' status with ALL required fields ---
        socketio.emit('power_status', {
            'id': power_id,
            'execution_id': execution_id,
            'status': 'finished',
            'message': 'Completed successfully.'
        })
    except Exception as e:
        # Report any errors that occur during execution
        print(f"Thread {execution_id}: Error during execution: {e}")
        import traceback
        traceback.print_exc()
        socketio.emit('power_status', {
            'id': power_id,
            'execution_id': execution_id,
            'status': 'error',
            'message': str(e)
        })
    finally:
        # Clean up the power from our tracking dictionary
        if execution_id in RUNNING_POWERS:
            del RUNNING_POWERS[execution_id]

# --- Endpoints ---
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
    # 1. Load the main power to get its function name
    main_power_data = power_repo.get_full_power(power_id)
    if not main_power_data:
        return jsonify({"error": "Power not found."}), 404

    main_function_name = main_power_data.get("function_name")

    # 2. Recursively get all required method definitions
    all_methods_dict = get_code_with_dependencies(power_repo, main_function_name)
    all_methods_code = "\n\n".join(all_methods_dict.values())

    # 3. Dynamically build the run_program method body
    # This creates the call with keyword arguments from the UI, e.g., height=25, material='STONE'
    run_program_args = ", ".join([f"{key}={repr(value)}" for key, value in runtime_params.items()])
    run_program_body = f"self.{main_function_name}({run_program_args})"

    # 4. Assemble the final, complete script string
    python_code = f"""
import numpy as np
import math
from mcshell.constants import *

class BlocklyProgramRunner:
    def __init__(self, action_implementer_instance,cancel_event=None,runtime_params={{}}):
        self.action_implementer = action_implementer_instance
        self.cancel_event = cancel_event
        self.runtime_params = runtime_params

    # --- Injected Method Definitions ---
{textwrap.indent(all_methods_code, '    ')}

    # --- Dynamically Generated Main Execution ---
    def run_program(self):
        if self.cancel_event and self.cancel_event.is_set(): return
{textwrap.indent(run_program_body, '        ')}
"""

    # --- Create a unique ID for this execution instance ---
    execution_id = str(uuid.uuid4())
    cancel_event = Event()

    thread = Thread(target=execute_power_in_thread, args=(
        power_id, execution_id, python_code, player_name, server_data, runtime_params, cancel_event
    ))
    thread.daemon = True
    thread.start()
    RUNNING_POWERS[execution_id] = {
        'thread': thread,
        'cancel_event': cancel_event,
        'power_id': power_id  # <-- STORE THE POWER ID
    }

    # We acknowledge the request was dispatched and include the unique execution_id.
    socketio.emit('power_status', {
            'id': power_id,
            'execution_id': execution_id,
            'status': 'dispatched',
            'message': 'Dispatched successfully.'
        })

    return jsonify({"status": "dispatched", "execution_id": execution_id})


@app.route('/api/cancel_power', methods=['POST'])
def cancel_power():
    """
    Cancels a running power and returns an HTML fragment representing the 'Idle'
    state, which includes the original 'Execute' button.
    """
    data = request.get_json() if request.is_json else request.form.to_dict()
    execution_id = data.get('execution_id')

    power_id = None
    if execution_id and execution_id in RUNNING_POWERS:
        power_to_cancel = RUNNING_POWERS[execution_id]
        power_id = power_to_cancel.get('power_id')
        power_to_cancel['cancel_event'].set()
        print(f"Cancellation signal sent for execution ID: {execution_id}")
        return jsonify({"status": "cancellation_requested"})
    if not power_id:
        return jsonify({"error": "Invalid or unknown execution_id"}), 404

@app.route('/api/block_materials')
def get_block_materials():
    """
    Serves the categorized dictionary of all block materials.
    """
    try:
        with open(MC_PICKER_MATERIALS_DATA_PATH, 'r') as f:
            material_data = json.load(f)
        return jsonify(material_data)
    except FileNotFoundError:
        return jsonify({"error": "Material data file not found."}), 404
    except Exception as e:
        return jsonify({"error": f"Could not load material data: {e}"}), 500

@app.route('/api/receive_invite', methods=['POST'])
def receive_invite():
    """
    Receives an invitation from another player and prints it to the
    local IPython console.
    """
    try:
        data = request.get_json()
        sender = data.get('sender_name', 'Another player')
        world = data.get('world_name', 'their world')
        host = data.get('host')
        port = data.get('port')
        password = data.get('password')
        fj_port = data.get('fj_port')

        # --- Print the formatted invitation to the user's console ---
        print("\n\n--- You have received a Minecraft world invitation! ---")
        print(f"From: {sender}")
        print(f"World: {world}")
        print("\nTo join their world, run the %mc_login command and input the following data:")
        print(f"Server Address: {host} ")
        print(f"Plugin Port: {fj_port} ")
        if password and port:
            print("\nTo join as an operator (admin), use:")
            print("\nIf you want to get server operator status, use the following data:")
            print(f"Server Port: {port}")
            print(f"Server Password: {password}")

        print("------------------------------------------------------\n")

        return jsonify({"success": True, "message": "Invitation displayed."})

    except Exception as e:
        print(f"Error processing invitation: {e}")
        return jsonify({"error": "Invalid invitation format."}), 400

# --- Control Panel ---
@app.route('/control')
def serve_control():
    """Serves the control panel UI (control.html)."""
    return send_from_directory(app.static_folder, 'control.html')

# --- Static File Serving ---
@app.route('/')
def serve_index():
    # Serve index.html from the 'dist' directory created by 'parcel build'
    return send_from_directory(current_app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Serve any other static files (JS, CSS) from the 'dist' directory
    return send_from_directory(current_app.static_folder, path)

