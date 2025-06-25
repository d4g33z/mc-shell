from flask import Blueprint, current_app, render_template_string

# 1. Create a Blueprint instance.
#    'powers_api' is the name of the blueprint.
#    __name__ helps Flask locate the blueprint.
#    url_prefix='/api' automatically prepends '/api' to all routes in this file.
control_bp = Blueprint('control_api', __name__, url_prefix='/api')


# 2. Move your power-related routes here.
#    Note that the decorator is now @powers_bp.route(...) instead of @app.route(...)


@control_bp.route('/control/widget/<power_id>')
def get_control_widget(power_id):
    """
    Loads a power's full metadata and renders the HTML for its
    interactive control widget.
    """
    player_id = current_app.config.get('MINECRAFT_PLAYER_NAME')
    power_repo = current_app.config.get('POWER_REPO')
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


