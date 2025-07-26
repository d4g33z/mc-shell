import os
import json
from flask import Blueprint, request, jsonify, make_response, current_app, render_template_string, session, send_file

from mcshell.constants import MC_CONTROL_LAYOUT_PATH

# 1. Create a Blueprint instance.
#    'powers_api' is the name of the blueprint.
#    __name__ helps Flask locate the blueprint.
#    url_prefix='/api' automatically prepends '/api' to all routes in this file.
powers_bp = Blueprint('powers_api', __name__, url_prefix='/api')


# 2. Move your power-related routes here.
#    Note that the decorator is now @powers_bp.route(...) instead of @app.route(...)

@powers_bp.route('/powers', methods=['POST'])
def save_new_power():
    """Saves a new power or updates an existing one."""
    player_id = current_app.config.get('MINECRAFT_PLAYER_NAME')
    power_repo = current_app.config.get('POWER_REPO')

    if not player_id or not power_repo:
        return jsonify({"error": "Not authorized or repository not configured"}), 500

    power_data = request.get_json()
    if not power_data or not power_data.get("name"):
        return jsonify({"error": "Invalid power data"}), 400

    try:
        power_id = power_repo.save_power(power_data)
        trigger_data = {
            "library-changed": f"Power '{power_data.get('name')}' was saved.",
            "closeSaveModal": True
        }
        headers = {"HX-Trigger": json.dumps(trigger_data)}
        return jsonify({"success": True, "power_id": power_id}), 201, headers
    except Exception as e:
        print(f"Error saving power for player {player_id}: {e}")
        return jsonify({"error": "An internal error occurred while saving the power."}), 500

# NEW ENDPOINT TO SERVE THE LAYOUT DEFINITION
@powers_bp.route('/control/layout', methods=['GET'])
def get_control_layout():
    # In a real app, this would load the layout for the specific player
    # For now, it reads a static file.
    try:
        # Assuming control_layout.json is in the project root
        return send_file(MC_CONTROL_LAYOUT_PATH, mimetype='application/json')
    except FileNotFoundError:
        print(f"{MC_CONTROL_LAYOUT_PATH} not found!")
        # Return a default empty layout if the file doesn't exist
        return jsonify({"grid": {"columns": 4}, "widgets": []})


@powers_bp.route('/powers', methods=['GET'])
def get_powers_list():
    """
    Gets the list of saved powers and renders the appropriate HTML fragment
    based on the 'view' query parameter ('editor' or 'control').
    """
    view_type = request.args.get('view', 'editor')

    player_id = current_app.config.get('MINECRAFT_PLAYER_NAME')
    power_repo = current_app.config.get('POWER_REPO')

    if not player_id or not power_repo:
        return "<p>Error: Not authorized</p>", 401

    powers_summary_list = power_repo.list_powers()

    # Group powers by category (logic remains the same)
    powers_by_category = {}
    for power in powers_summary_list:
        category = power.get('category', 'Uncategorized')
        if category not in powers_by_category:
            powers_by_category[category] = []
        powers_by_category[category].append(power)

    # --- Select the correct template based on the view type ---
    if view_type == 'control':

        # Call the new method to get all data needed for the control UI
        all_powers_list = power_repo.list_full_powers()
        # Convert the list into a dictionary keyed by power_id for easy lookup on the client
        powers_dict = {p['power_id']: p for p in all_powers_list if 'power_id' in p}

        print(f"Serving full power data dictionary for player '{player_id}' for control UI.")
        return jsonify(powers_dict)

    else:  # Default to the 'editor' view
        # Use the detailed template for the editor sidebar
        template_string = """
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
        html_response_string = render_template_string(template_string, categories=powers_by_category)

    # Create the final response with no-cache headers
    response = make_response(html_response_string)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response


@powers_bp.route('/power/<power_id>', methods=['GET'])
def get_power_detail(power_id):
    """
    Gets the full JSON data for a single power, used by the editor to load
    a workspace. The data is returned in an HX-Trigger header.
    """
    mode = request.args.get('mode', 'replace')

    player_id = current_app.config.get('MINECRAFT_PLAYER_NAME')
    power_repo = current_app.config.get('POWER_REPO')

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


@powers_bp.route('/power/<power_id>', methods=['DELETE'])
def delete_power_by_id(power_id):
    """Deletes a specific power from the user's library."""
    player_id = current_app.config.get('MINECRAFT_PLAYER_NAME')
    power_repo = current_app.config.get('POWER_REPO')

    if not player_id or not power_repo:
        return jsonify({"error": "Not authorized or repository not configured"}), 500

    print(f"Received request to delete power '{power_id}' for player '{player_id}'")

    try:
        success = power_repo.delete_power(power_id)
        if success:
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
