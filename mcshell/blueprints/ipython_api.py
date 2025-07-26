import sys
from io import StringIO
from flask import Blueprint, jsonify, current_app, request
from IPython.utils.capture import capture_output
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

    try:
        # Use run_line_magic to execute the command
        # Use IPython's own capture_output context manager.
        # It reliably captures all output generated within the 'with' block.
        with capture_output() as captured:
            try:
                magic_name = command.lstrip('%')
                shell.run_line_magic(magic_name, arguments)
            except Exception as e:
                # Also capture any exceptions that occur during execution
                print(f"\n--- ERROR DURING MAGIC EXECUTION ---\n{e}")

        # The captured stdout and stderr are available on the object
        output = captured.stdout

        # You can still write to the original console if you want
        sys.stdout.write(output)

        return jsonify({"success": True, "output": output})
    except Exception as e:
        # If the magic itself throws an error, capture it
        print(f"Error executing magic command '{command}': {e}")
        return jsonify({"error": str(e)}), 500

