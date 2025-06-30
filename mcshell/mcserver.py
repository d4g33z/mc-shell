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
    # return "Execute"
    # #TODO: how can I avoid returning html???
    # running_state_html = f"""
    # <div class="widget-main-actions" hx-swap-oob="true" id="actions-{power_id}">
    #     <div class="power-status">Status: <span class="running">Running...</span></div>
    #     <button class="btn-small btn-danger cancel-btn"
    #             hx-post="/api/cancel_power"
    #             hx-ext="json-enc"
    #             hx-vals='{{"execution_id": "{execution_id}"}}'
    #             hx-target="#actions-{power_id}"
    #             hx-swap="outerHTML">
    #         Cancel
    #     </button>
    # </div>
    # """
    # return running_state_html

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
    # socketio.emit('power_status', {'id': execution_id, 'status': 'running'})

    try:
        # We need the app context for config
        with app.app_context():
            #we could pass cancel to MCPlayer here and make sword hits cancelable
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
            # You could pass the cancel_event to the runner if methods can check it.
            # runner.cancel_event = cancel_event
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
            # if cancel_event.is_set():
            #     print(f"Thread {execution_id}: Execution was cancelled.")
            #     # --- Send the 'cancelled' status with ALL required fields ---
            #     socketio.emit('power_status', {
            #         'id': power_id,
            #         'execution_id': execution_id,
            #         'status': 'cancelled',
            #         'message': 'Cancelled by user.'
            #     })
            #     return
            # if cancel_event.is_set():
            #     print(f"Thread {execution_id}: Execution was cancelled.")
            #     socketio.emit('power_status', {'id': execution_id, 'status': 'cancelled'})
            #     return

        print(f"Thread {execution_id}: Execution completed successfully.")
        # --- Send the 'finished' status with ALL required fields ---
        socketio.emit('power_status', {
            'id': power_id,
            'execution_id': execution_id,
            'status': 'finished',
            'message': 'Completed successfully.'
        })
        # print(f"Thread {execution_id}: Execution completed successfully.")
        # socketio.emit('power_status', {'id': execution_id, 'status': 'finished'})
    except Exception as e:
        # Report any errors that occur during execution
        print(f"Thread {execution_id}: Error during execution: {e}")
        import traceback
        traceback.print_exc()
        # socketio.emit('power_status', {'id': execution_id, 'status': 'error', 'message': str(e)})
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

@app.route('/api/cancel_power', methods=['POST'])
def cancel_power():
    """
    Cancels a running power and returns an HTML fragment representing the 'Idle'
    state, which includes the original 'Execute' button.
    """
    data = request.get_json() if request.is_json else request.form.to_dict()
    execution_id = data.get('execution_id')

    # --- THIS IS THE FIX ---
    # We need to find the original power_id to rebuild the 'Execute' button.
    # This requires a small change to how we store running powers.
    power_id = None
    if execution_id and execution_id in RUNNING_POWERS:
        power_to_cancel = RUNNING_POWERS[execution_id]
        power_id = power_to_cancel.get('power_id')
        power_to_cancel['cancel_event'].set()
        print(f"Cancellation signal sent for execution ID: {execution_id}")
        return jsonify({"status": "cancellation_requested"})
    if not power_id:
        return jsonify({"error": "Invalid or unknown execution_id"}), 404
        # return "<div class='power-status has-error'>Error: Could not find power to cancel.</div>"
    #
    # # Rebuild the original "Execute" button state as an HTML fragment.
    # idle_state_html = f"""
    # <div class="widget-main-actions" id="actions-{power_id}">
    #     <div class="power-status">Status: Cancelled</div>
    #     <button class="execute-btn"
    #             hx-post="/api/execute_power"
    #             hx-include="#form-{power_id}"
    #             hx-vals='{{"power_id": "{power_id}"}}'
    #             hx-target="#actions-{power_id}"
    #             hx-swap="outerHTML">
    #         Execute
    #     </button>
    # </div>
    # """
    # return idle_state_html

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