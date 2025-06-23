import ast
import threading
from threading import Thread, Event
from io import StringIO

from flask import Flask, request, jsonify, send_from_directory, session
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

@app.route('/execute_power', methods=['POST'])
def execute_power():
    """
    Executes a saved power by its ID.
    The client no longer sends the code, only the ID of the power to run.
    """
    player_name = app.config.get('MINECRAFT_PLAYER_NAME')
    power_repo = app.config.get('POWER_REPO')

    data = request.get_json()
    power_id = data.get('power_id')

    if not all([power_id, player_name]):
        return jsonify({"error": "Missing power_id or not authorized"}), 400

    # 1. Load the full power data, including the python_code
    full_power_data = power_repo.get_full_power(power_id)

    if not full_power_data:
        return jsonify({"error": "Power not found"}), 404

    python_code = full_power_data.get("python_code")

    # 2. The rest of the logic remains the same: start the thread with this code
    server_data = app.config.get('MCSHELL_SERVER_DATA')
    # ... create cancel_event, start thread ...
    # thread = Thread(target=execute_power_thread, args=(python_code, ...))
    # ...
    return jsonify({"status": "dispatched", "power_id": power_id})

@app.route('/execute_power_by_name', methods=['POST'])
def execute_power_by_name():
    power_repo = app.config.get('POWER_REPO')
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
    player_id = app.config.get('MINECRAFT_PLAYER_NAME')
    power_repo = app.config.get('POWER_REPO')

    if not power_repo or not player_id:
        trigger_data = {"showError": {"errorMessage": "Server not fully configured."}}
        return make_response("", 500, {"HX-Trigger": json.dumps(trigger_data)})

    power_data = request.get_json()
    if not power_data or not power_data.get("name"):
        return jsonify({"error": "Invalid power data"}), 400

    try:
        power_id = power_repo.save_power(power_data)

        # --- CORRECTED: Send multiple triggers back to the client ---
        # 1. Create a dictionary with ALL events we want to fire on the client.
        trigger_data = {
            # "power-saved": f"A power with id {power_id} was saved.",
            "library-changed": f"Power {power_id} was saved.",
            "closeSaveModal": True # This event will tell Alpine.js to close the modal.
        }

        # 2. Convert the dictionary to a JSON string for the header.
        headers = {"HX-Trigger": json.dumps(trigger_data)}

        # 3. Return the response with the headers.
        return jsonify({"success": True, "power_id": power_id}), 201, headers

    except Exception as e:
        print(f"Error saving power for player {player_id}: {e}")
        return jsonify({"error": "An internal error occurred while saving the power."}), 500

@app.route('/api/power/<power_id>', methods=['DELETE'])
def delete_power_by_id(power_id):
    player_id = app.config.get('MINECRAFT_PLAYER_NAME')
    power_repo = app.config.get('POWER_REPO')

    if not player_id or not power_repo:
        return jsonify({"error": "Not authorized or repository not configured"}), 500

    print(f"Received request to delete power '{power_id}' for player '{player_id}'")

    try:
        success = power_repo.delete_power(power_id)
        if success:
            # --- THIS IS THE FIX ---
            # Instead of an empty response, we now trigger the 'library-changed' event.
            trigger_data = {"library-changed": f"Power {power_id} was deleted."}
            headers = {"HX-Trigger": json.dumps(trigger_data)}

            # Return a 200 OK. The body can be empty. The header does the work.
            return "", 200, headers
        else:
            return jsonify({"error": "Power not found"}), 404
    except Exception as e:
        print(f"Error deleting power {power_id}: {e}")
        return jsonify({"error": "An internal error occurred during deletion."}), 500

@app.route('/api/control/powers', methods=['GET'])
def get_powers_for_control_panel():
    """
    Fetches power summaries and renders them as a simple list with "Add" buttons,
    specifically for the control UI's library panel.
    """
    player_id = app.config.get('MINECRAFT_PLAYER_NAME')
    power_repo = app.config.get('POWER_REPO')
    if not player_id or not power_repo:
        return "<p>Error: Not authorized</p>", 401

    powers_summary_list = power_repo.list_powers()

    # This template is simpler than the editor's.
    # Its only job is to provide a button to add a widget to the control grid.
    control_library_template = """
    <h4>Available Powers</h4>
    <ul>
    {% for power in powers %}
        <li class="control-library-item">
            <span>{{ power.name }}</span>
            <button class="btn-small"
                    hx-get="/api/control_widget/{{ power.power_id }}"
                    hx-target="#control-grid"
                    hx-swap="beforeend">
                Add to Grid
            </button>
        </li>
    {% endfor %}
    </ul>
    """

    html_response_string = render_template_string(
        control_library_template,
        powers=powers_summary_list
    )

    response = make_response(html_response_string)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/control_widget/<power_id>')
def get_control_widget(power_id):
    """
    Loads a power's full metadata and renders the HTML for its
    interactive control widget.
    """
    player_id = app.config.get('MINECRAFT_PLAYER_NAME')
    power_repo = app.config.get('POWER_REPO')
    power_data = power_repo.get_full_power(power_id)

    if not power_data:
        return "<div class='error'>Power not found.</div>", 404

    # This Jinja2 template dynamically builds the widget based on the power's metadata
    widget_template = """
    <div class="power-widget" id="widget-{{ power.power_id }}" x-data>
        <div class="power-header">
            <span class="power-name">{{ power.name }}</span>
            </div>

        <form class="power-params" id="form-{{ power.power_id }}">
            {% for param in power.parameters %}
                <div class="param-control">
                    <label for="param-{{ power.power_id }}-{{ param.name }}">{{ param.name }}:</label>
                    
                    {# Dynamically render the correct input based on parameter type #}
                    {% if param.type == 'Number' %}
                        <div class="param-slider">
                            <input type="range" name="{{ param.name }}" value="{{ param.default }}" min="1" max="100"
                                   oninput="this.nextElementSibling.value = this.value">
                            <output>{{ param.default }}</output>
                        </div>
                    {% elif param.type == 'Block' %}
                        <select name="{{ param.name }}">
                            {# This should be populated with a relevant list of blocks #}
                            <option value="STONE" {% if param.default == 'STONE' %}selected{% endif %}>Stone</option>
                            <option value="OAK_PLANKS" {% if param.default == 'OAK_PLANKS' %}selected{% endif %}>Oak Planks</option>
                            <option value="GLASS" {% if param.default == 'GLASS' %}selected{% endif %}>Glass</option>
                            <option value="DIAMOND_BLOCK" {% if param.default == 'DIAMOND_BLOCK' %}selected{% endif %}>Diamond Block</option>
                        </select>
                    {# Add more elif cases here for Entity, MinecraftColour, String etc. #}
                    {% else %}
                        <input type="text" name="{{ param.name }}" value="{{ param.default or '' }}">
                    {% endif %}
                </div>
            {% endfor %}
        </form>
        
        <div class="power-status" id="status-{{ power.power_id }}">Status: Idle</div>
        
        <button class="execute-btn"
                hx-post="/api/execute_power"
                hx-include="#form-{{ power.power_id }}"
                hx-vals='{"power_id": "{{ power.power_id }}"}'
                hx-target="#status-{{ power.power_id }}"
                hx-swap="innerHTML">
            Execute
        </button>
    </div>
    """

    return render_template_string(widget_template, power=power_data)

@app.route('/api/editor/powers', methods=['GET'])
def get_powers_for_editor_sidebar():
    """
    Fetches the list of saved powers for the authorized player,
    groups them by category, and renders them as an HTML fragment using Jinja2.
    """
    # 1. Get the repository instance from the app config. It's already player-specific.
    power_repo = app.config.get('POWER_REPO')
    player_id = app.config.get('MINECRAFT_PLAYER_NAME') # Still useful for logging/context

    if not power_repo or not player_id:
        # Error handling remains the same
        trigger_data = {"showError": {"errorMessage": "Server not fully configured."}}
        return make_response("", 500, {"HX-Trigger": json.dumps(trigger_data)})

    # 2. Fetch the flat list of power summaries from the repository.
    #    No player_id is passed to the method, as requested.
    powers_summary_list = power_repo.list_powers()

    if not powers_summary_list:
        return "<p style='padding: 0 10px; color: #666;'>No powers saved yet. Create one!</p>"

    # 3. Process the data: group the flat list of powers by category.
    powers_by_category = {}
    for power in powers_summary_list:
        category = power.get('category', 'Uncategorized')
        if category not in powers_by_category:
            powers_by_category[category] = []
        powers_by_category[category].append(power)

    # 4. Define the Jinja2 template for rendering the library.
    #    This template includes Alpine.js directives for collapsible sections.
# Gemini, come on!


    library_template_string = """
    {% for category, powers in categories.items()|sort %}
      <div class="power-category" x-data="{ open: true }">
        <h3 @click="open = !open">
          <span class="category-toggle" x-text="open ? '▼' : '▶'"></span>
          {{ category }} ({{ powers|length }})
        </h3>
        <ul class="power-item-list" x-show="open" x-transition>
          {% for power in powers %}
            <li class="power-item" x-data="{ open: false }" id="power-item-{{ power.power_id }}">
              <div class="power-item-header" @click="open = !open">
                <span class="power-toggle" x-text="open ? '▼' : '▶'"></span>
                <span class="power-name">{{ power.name }}</span>
              </div>
              <div class="power-item-details" x-show="open" x-transition>
                <p class="power-description">{{ power.description or 'No description.' }}</p>
                <div class="power-item-actions">

                  <button class="btn-small"
                          hx-get="/api/power/{{ power.power_id }}?mode=replace"
                          hx-swap="none"
                          title="Clear workspace and load this power">
                      Load (Replace)
                  </button>
                  
                  <button class="btn-small"
                          hx-get="/api/power/{{ power.power_id }}?mode=add"
                          hx-swap="none"
                          title="Add this power's blocks to the current workspace">
                      Add to Workspace
                  </button> 
                  
                  <button class="btn-small btn-danger"
                          @click="$dispatch('open-delete-confirm', { 
                              powerId: '{{ power.power_id }}', 
                              powerName: '{{ power.name | replace("'", "\\'") }}' 
                          })">
                      Delete
                  </button>
                </div>
              </div>
            </li>
          {% endfor %}
        </ul>
      </div>
    {% endfor %}
    """

    # 5. Render the HTML fragment using the template and the grouped data.
    html_response_string = render_template_string(
        library_template_string,
        categories=powers_by_category
    )

    # 6. Create the final response with headers to prevent caching.
    response = make_response(html_response_string)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

@app.route('/api/power/<power_id>', methods=['GET'])
def get_power_detail(power_id):
    """
    Gets the full data for a single power by its ID.
    Returns the data in an HX-Trigger header for the client-side JS to handle.
    """

    # Get the 'mode' from the URL's query string (e.g., ?mode=add).
    # Default to 'replace' if the parameter is missing for any reason.
    mode = request.args.get('mode', 'replace')

    player_id = app.config.get('MINECRAFT_PLAYER_NAME')
    power_repo = app.config.get('POWER_REPO')

    if not player_id or not power_repo:
        # Handle error case
        err_trigger = {"showError": {"errorMessage": "Server or player not configured."}}
        return make_response("", 401, {"HX-Trigger": json.dumps(err_trigger)})

    full_power_data = power_repo.get_full_power(power_id)

    if not full_power_data:
        err_trigger = {"showError": {"errorMessage": f"Power with ID {power_id} not found."}}
        return make_response("", 404, {"HX-Trigger": json.dumps(err_trigger)})

    # --- NEW: If replacing, set this as the current power in the session ---
    if mode == 'replace':
        session['current_power'] = {
            "power_id": power_id,
            "name": full_power_data.get("name"),
            "description": full_power_data.get("description"),
            "category": full_power_data.get("category")
        }
        print(f"Session 'current_power' set to: {full_power_data.get('name')}")
    # --- The Htmx Event Trigger Response ---
    # We are defining a custom event 'loadPower' and passing the full power data
    # and the loading 'mode' inside the event's detail.
    trigger_data = {
        "loadPower": {
            "powerData": full_power_data,
            "mode": mode # Signal to the client to replace the workspace
        }
    }

    headers = {"HX-Trigger": json.dumps(trigger_data)}

    # We don't need to send a body, just the trigger header. Status 204 No Content is perfect.
    return "", 204, headers

@app.route('/api/ipython_magic', methods=['POST'])
def execute_ipython_magic():
    """Receives a magic command and its arguments to be executed in the shell."""
    data = request.get_json()
    command = data.get('command')
    arguments = data.get('arguments', '') # Arguments are the rest of the line

    if not command:
        return jsonify({"error": "No command provided"}), 400

    # Retrieve the shell instance we stored in the config
    shell = app.config.get('IPYTHON_SHELL')
    if not shell:
        return jsonify({"error": "IPython shell not available in server."}), 500

    # --- Capture stdout to send back to the client ---
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()

    try:
        # Use run_line_magic to execute the command
        # It takes the magic name (without %) and the rest of the line as an argument string
        magic_name = command.lstrip('%')
        shell.run_line_magic(magic_name, arguments)

        # Get the output that was printed to the console
        output = redirected_output.getvalue()
        old_stdout.write(output)
        return jsonify({"success": True, "output": output})

    except Exception as e:
        # If the magic itself throws an error, capture it
        print(f"Error executing magic command '{command}': {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        # ALWAYS restore stdout
        sys.stdout = old_stdout

# --- Static File Serving ---

@app.route('/')
def serve_index():
    # Serve index.html from the 'dist' directory created by 'parcel build'
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Serve any other static files (JS, CSS) from the 'dist' directory
    return send_from_directory(app.static_folder, path)




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