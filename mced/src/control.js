import Alpine from 'alpinejs';
import Sortable from 'sortablejs';

import htmx from 'htmx.org'

import { io } from "socket.io-client"; // <-- Import the io function

// --- 1. Establish the connection to your Flask-SocketIO server ---
// const socket = io("http://localhost:5001"); // Use the address of your Python server
const socket = io(); // Use the address of your Python server

socket.on('connect', () => {
    console.log('Control UI connected to backend server with Socket.IO:', socket.id);
});

socket.on('disconnect', () => {
    console.log('Control UI disconnected from Socket.IO server.');
});

const WIDGET_REGISTRY = {};

// --- 1. Define an Alpine Store for Shared Data ---
document.addEventListener('alpine:init', () => {
    Alpine.store('materials', {
        groups: {}, // This will hold the categorized block data

        load() {
            fetch('/api/block_materials')
                .then(res => res.json())
                .then(data => {
                    this.groups = data;
                    console.log("Shared material data loaded into Alpine store.");
                });
        }
    });
});


// --- 2. Define the Component for the Custom Picker ---
function materialPicker(defaultSelection, paramName) {
    return {
        isOpen: false,
        selected: defaultSelection || 'STONE',
        filter: '',
        paramName: paramName, // Store the parameter name for the hidden input
    };
}
window.materialPicker = materialPicker;




function powerWidget(initialPowerData) {
    return {
        // Remember: this the data from the power library !!!
        // i.e {name,description,category, power_id,blockly_json,python_code,parameters}
        power: initialPowerData,
        formValues: {},
        showAdminControls: false,
        currentExecutionId: null,

        init() {
            // Your existing init logic to set up formValues
            if (this.power && this.power.parameters) {
                this.power.parameters.forEach(param => {
                    this.formValues[param.name] = param.default;
                });
            }

            // Your existing event listener for edit mode
            window.addEventListener('control-mode-changed', (event) => {
                this.showAdminControls = event.detail.editing;
            });

            WIDGET_REGISTRY[this.power.power_id] = this;
        },

       removeWidget() {
            this.$dispatch('remove-widget-from-grid', { powerId: this.power.power_id });
            WIDGET_REGISTRY[this.power.power_id] = null;
        },

        updateStatus(newStatus, executionId, message = '') {
            console.log(`updateStatus called with: status=${newStatus}, executionId=${executionId}`);
            this.status = newStatus;
            this.errorMessage = message;

            // The executionId should ONLY have a value when the power is running.
            // When it's finished, cancelled, or errored, it must be cleared.
            if (newStatus === 'running') {
                this.currentExecutionId = executionId;
            } else {
                this.currentExecutionId = null;
            }
        },

        executePower() {
            // Use this.$refs to get the form element reliably
            const formElement = this.$refs.paramsForm;
            if (!formElement) {
                console.error("Could not find the parameters form for this widget!");
                return;
            }

            const formData = new FormData(formElement);
            const params = Object.fromEntries(formData.entries());
            params.power_id = this.power.power_id;

            // Update status immediately for a responsive UI
            this.status = 'running';

            fetch('/api/execute_power', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params)
            })
            .then(res => res.json())
            .then(data => {
                if (data.execution_id) {
                    // The server confirms the start and gives us the real ID
                    this.currentExecutionId = data.execution_id;
                    console.log(`Power execution started with ID: ${this.currentExecutionId}`);
                } else {
                    this.updateStatus('error', null, data.error || 'Failed to start execution.');
                }
            })
            .catch(err => {
                console.error('Fetch error during execution:', err);
                this.updateStatus('error', null, 'Network error.');
            });
        },

        cancelPower() {
            if (!this.currentExecutionId) return;

            console.log(`Sending cancellation for execution ID: ${this.currentExecutionId}`);
            fetch('/api/cancel_power', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ execution_id: this.currentExecutionId })
            });
            // The UI will update automatically when the 'cancelled' status
            // is received via the WebSocket.
        }

    };
}
window.powerWidget = powerWidget;


// The data and methods for our main control panel component
function controlPanel() {
  return {
    powers: {}, // Will hold the data for all available powers
    layout: { grid: { columns: 4 }, widgets: [] }, // Will hold the layout data
    isEditing: false, // Toggles edit mode for drag-and-drop
    sortableInstance: null, // To hold our SortableJS instance
    // materialGroups: {}, // To hold materials for control UI
    // NEW: A dictionary to hold the live status of each power widget
    // e.g., { "power-id-123": { status: 'running', message: '' }, ... }
    powerStatuses: {},

      init() {

      // Tell the materials store to load its data
      Alpine.store('materials').load();
      console.log('Initializing control panel...');

      // The socket listener now lives inside the init method and updates our state.
          // // --- Set up a global listener for power status updates ---
          if (window.socket) {
              socket.on('power_status', (data) => {
                  console.log('Received power status update:', data);
                  this.powerStatuses[data.id] = {
                      status: data.status,
                      message: data.message || '',
                      execution_id: data.execution_id || null
                  };
                  if (data.status === 'dispatched') {
                      return
                  }
                  else  {
                      // const widgetInstance= document.getElementById(`widget-${data.id}`);
                      const widgetInstance = WIDGET_REGISTRY[data.id]
                      if (widgetInstance) {
                          // If we found it, call its updateStatus method directly.
                          // This is guaranteed to work and avoids any DOM race conditions.
                          widgetInstance.updateStatus(data.status, data.execution_id, data.message || '');
                      } else {
                          console.warn(`Could not find a registered widget for power ID: ${data.id}`);
                      }
                  }
              });
          }


      // --- CONSOLIDATED $watch --
      // This single watcher handles ALL logic related to the isEditing state change.
      this.$watch('isEditing', (isNowEditing) => {
        console.log(`Edit mode changed to: ${isNowEditing}`);

        // 1. Enable or disable SortableJS based on the new state.
        if (this.sortableInstance) {
          console.log(`Setting drag-and-drop to ${isNowEditing ? 'ENABLED' : 'DISABLED'}.`);
          this.sortableInstance.option('disabled', !isNowEditing);
        }

        // 2. Broadcast the global event for child components to hear.
        console.log(`Broadcasting event: control-mode-changed, editing: ${isNowEditing}`);
        window.dispatchEvent(new CustomEvent('control-mode-changed', {
            detail: { editing: isNowEditing }
        }));
      });
      // --- END OF CONSOLIDATION ---

      // Fetch both layout and power data when the component loads
      Promise.all([
        fetch('/api/control/layout').then(res => res.json()),
        fetch('/api/powers?view=control').then(res => res.json()),
        // fetch('/api/block_materials').then(res => res.json()) // <-- NEW FETCH
      ]).then(([layoutData, powersData, materialData]) => {
        this.layout = layoutData;
        this.powers = powersData;
        // this.materialGroups = materialData; // <-- STORE THE DATA
        console.log('Layout, powers, and material data loaded.');

        // Initialize drag-and-drop after the next DOM update
        this.$nextTick(() => {
          // Use the standard document.getElementById to get the grid element.
          const grid = document.getElementById('power-grid');

          if (grid) {
            console.log("Alpine has rendered the widgets. Now processing them with htmx...");
             // 1. Tell Alpine.js to initialize any x-data components inside the new widget
             window.Alpine.initTree(grid);
            // 1. Tell htmx to scan the grid and activate all hx-* attributes inside it.
            htmx.process(grid);

            this.sortableInstance = new Sortable(grid, {
              animation: 150,

              // onStart is called when a drag begins.
              onStart: (event) => {
                // Add x-ignore to the grid. This tells Alpine to completely
                // ignore this element and all its children. Alpine will not
                // initialize any new elements added inside it.
                grid.setAttribute('x-ignore', '');
                console.log('Drag started: Applying x-ignore to grid.');
              },

              // onEnd is called when a drag operation finishes.
              onEnd: (event) => {
                // Remove x-ignore so Alpine can manage the elements again.
                grid.removeAttribute('x-ignore');
                console.log('Drag ended: Removing x-ignore from grid.');

                // Your logic to update the layout array order will go here.
                // For example:
                // const widgetIds = Array.from(grid.children).map(child => child.__x.getUnobservedData().widget.power_id);
                // this.layout.widgets = widgetIds.map(id => ({ power_id: id, position: [] }));
              }
            });
            this.sortableInstance.option('disabled', true);
          } else {
              console.error("Could not find #power-grid to initialize SortableJS.");
          }
        });
      });


    },

    // NEW: Helper for widgets to get their current status
    getStatusForWidget(powerId) {
        return this.powerStatuses[powerId] || { status: 'Idle', message: '' , execution_id: null};
    },

   // NEW METHOD to fetch the latest power data
    refreshPowersData() {
      console.log("Refreshing full powers data from server...");
      fetch('/api/powers?view=control')
        .then(res => res.json())
        .then(powersData => {
          this.powers = powersData;
          console.log('Powers data has been updated.');
        });
    },

    // A helper to get the power data for a widget from the main powers dictionary
    getPowerData(widget) {
      return this.powers[widget.power_id] || { name: 'Unknown Power', parameters: [] };
    },

    /**
     * Adds a new widget to the client-side layout data, then uses $nextTick
     * to initialize htmx on the new DOM element after Alpine has rendered it.
     * @param {string} powerId The ID of the power widget to add.
     */
    addWidget(powerId) {
        if (!powerId || this.layout.widgets.some(w => w.power_id === powerId)) {
            if (this.layout.widgets.some(w => w.power_id === powerId)) {
                alert('This power is already on your control grid.');
            }
            return;
        }

        // 1. Change the state: Add the new widget's data to the array.
        //    Alpine will see this and schedule a DOM update.
        console.log(`Adding widget for power ID: ${powerId} to layout data.`);
        this.layout.widgets.push({ power_id: powerId, position: [] });

        // 2. Use $nextTick to run code AFTER the DOM has been updated.
        this.$nextTick(() => {
            console.log('Alpine has updated the DOM. Now processing the new widget with htmx.');

            // Find the grid and then find the very last widget element, which is the one we just added.
            const grid = document.getElementById('power-grid');
            if (grid && grid.lastElementChild) {
                // 3. Call htmx.process() on ONLY the new element.
                htmx.process(grid.lastElementChild);
                console.log('New widget processed by htmx.');
            }
        });
    },

    removeWidget(powerId) {
        // Filter the widgets array to remove the one with the matching ID
        this.layout.widgets = this.layout.widgets.filter(w => w.power_id !== powerId);
        console.log(`Removed widget for power: ${powerId}`);
    }

  }
}

window.socket = socket
window.controlPanel = controlPanel;
window.Alpine = Alpine;
Alpine.start();