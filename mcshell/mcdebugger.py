from flask import Flask, request, jsonify
from flask_cors import CORS
from IPython import get_ipython # To access the current IPython instance

import logging,threading

app = Flask(__name__)
CORS(app)

# --- Suppress Flask's Default Console Logging ---
flask_logger = logging.getLogger('werkzeug') # Get Werkzeug logger (Flask's dev server)
flask_logger.setLevel(logging.ERROR) # Set Werkzeug logger level to ERROR or WARNING (or higher)
#flask_logger.setLevel(logging.DEBUG) # Set Werkzeug logger level to ERROR or WARNING (or higher)
# Alternatively, to completely remove the default Werkzeug console handler:
# flask_logger.handlers = [] # Remove all handlers, including console

@app.route('/ipython_magic', methods=['POST'])
def execute_ipython_magic_api():
    data = request.get_json()
    magic_command = data.get('command')  # e.g., '%my_magic' or '%ls'
    arguments = data.get('arguments', '') # Arguments as a string
    if not magic_command:
        return jsonify({"error": "Command is required"}), 400

    ipython = get_ipython()  # Get the current IPython shell instance

    if ipython is None:
        return jsonify({"error": "IPython environment not available"}), 500

    try:
        ipython.magic(f"{magic_command} {arguments}")  # Execute magic command
        return jsonify({"output": "Command executed successfully. See IPython console for output."})
    except Exception as e:
        return jsonify({"error": f"Error executing magic: {str(e)}"}), 500

# TODO: create a paper server control

debug_server_thread = None # Global variable to hold the server thread

def start_debug_server():
    """Starts the Flask development server in a separate thread."""
    global debug_server_thread # Access the global server_thread variable
    if debug_server_thread is None or not debug_server_thread.is_alive():
        debug_server_thread = threading.Thread(target=app.run, kwargs={'debug': True, 'use_reloader': False}) # Run app.run in thread, disable reloader!
        debug_server_thread.daemon = True # Allow main thread to exit even if server thread is running
        debug_server_thread.start()
    else:
        pass


def stop_debug_server():
    """Gracefully stops the Flask development server."""
    global debug_server_thread
    if debug_server_thread and debug_server_thread.is_alive():
        # Flask's dev server doesn't have a clean stop method, so we use shutdown_server (from Flask examples)
        func = request.environ.get('werkzeug.server.shutdown') # Get shutdown function from Werkzeug environment
        if func:
            func() # Call shutdown function if available
        else:
            pass
        debug_server_thread.join(timeout=2) # Wait for thread to finish briefly
        if debug_server_thread.is_alive():
            pass
        debug_server_thread = None # Reset server_thread
    else:
        pass