import sys
from io import StringIO
from flask import Blueprint, jsonify, current_app, request
ipython_bp = Blueprint('ipython_api',__name__,url_prefix='/api')

@ipython_bp.route('/ipython_magic', methods=['POST'])
def execute_ipython_magic():
    """Receives a magic command and its arguments to be executed in the shell."""
    data = request.get_json()
    command = data.get('command')
    arguments = data.get('arguments', '') # Arguments are the rest of the line

    if not command:
        return jsonify({"error": "No command provided"}), 400

    # Retrieve the shell instance we stored in the config
    shell = current_app.config.get('IPYTHON_SHELL')
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

