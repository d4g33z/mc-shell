from flask import Blueprint, current_app, render_template_string, make_response

# 1. Create a Blueprint instance.
#    'powers_api' is the name of the blueprint.
#    __name__ helps Flask locate the blueprint.
#    url_prefix='/api' automatically prepends '/api' to all routes in this file.
control_bp = Blueprint('control_api', __name__, url_prefix='/api')


@control_bp.route('/control/powers_library', methods=['GET'])
def get_powers_for_control_library():
    """
    Renders a simple list of available powers, each with an Alpine.js
    button to add it to the control grid's client-side state.
    """
    power_repo = current_app.config.get('POWER_REPO')
    powers_summary_list = power_repo.list_powers()

    # This template's button calls the 'addWidget' method on our Alpine component
    library_template = """
    <ul class="control-library-list">
    {% for power in powers %}
        <li class="control-library-item">
            <span>{{ power.name }}</span>
            <button class="btn-small"
                    @click="$dispatch('add-widget-to-grid', '{{ power.power_id }}')">
                + Add
            </button>
        </li>
    {% endfor %}
    </ul>
    """
    html_response_string = render_template_string(library_template, powers=powers_summary_list)
    response = make_response(html_response_string)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response