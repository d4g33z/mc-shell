import Alpine from 'alpinejs';
import Sortable from 'sortablejs'; // For drag-and-drop later

import htmx from 'htmx.org'
// import 'htmx.org'; // Keep for executing powers
// 1. Import all exports from the htmx.org package into a namespace variable called `htmx`.
// import * as htmx from 'htmx.org';
// import 'htmx-ext-json-enc';

// 2. Manually attach the imported htmx object to the global window object.
//    This makes it accessible to the hx-* attributes in your HTML.
// window.htmx = htmx;

import { io } from "socket.io-client"; // <-- Import the io function

// --- 1. Establish the connection to your Flask-SocketIO server ---
const socket = io("http://localhost:5001"); // Use the address of your Python server

socket.on('connect', () => {
    console.log('Control UI connected to backend server with Socket.IO:', socket.id);
});

socket.on('disconnect', () => {
    console.log('Control UI disconnected from Socket.IO server.');
});

// --- 2. Set up a global listener for power status updates ---
socket.on('power_status', (data) => {
    console.log('Received power status update:', data);
    // data should look like: {id: "power-id-abc", execution_id: "...", status: "finished"}

    // Find the specific widget on the page that this update is for
    const widgetElement = document.getElementById(`widget-${data.id}`);
    if (widgetElement) {
        // Dispatch a custom event specifically on this element
        // The widget's Alpine component will be listening for this.
        widgetElement.dispatchEvent(new CustomEvent('update-status', {
            detail: { status: data.status, message: data.message || '' },
            bubbles: false // The event doesn't need to bubble
        }));
    }
});
/**
 * Creates the data object for a single power widget component.
 * It is now self-contained and listens for global state changes.
 */
function powerWidget(initialPowerData) {
    return {
        power: initialPowerData,
        formValues: {},
        showAdminControls: false, // Each widget tracks its own "delete button" visibility
       // NEW: Add a state variable to track the widget's status
        status: 'Idle',
        // We can also store the execution_id when a power is running
        currentExecutionId: null,

        init() {
            // Initialize form values from parameter defaults
            if (this.power && this.power.parameters) {
                this.power.parameters.forEach(param => {
                    this.formValues[param.name] = param.default;
                });
            }

            // Listen for the global mode change event
            window.addEventListener('control-mode-changed', (event) => {
                this.showAdminControls = event.detail.editing;
            });
        },
        // We can add a helper method to update the status
        updateStatus(newStatus, executionId = null) {
            this.status = newStatus;
            this.currentExecutionId = executionId;
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

    init() {

        console.log('Initializing control panel...');

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
        fetch('/api/powers?view=control').then(res => res.json())
      ]).then(([layoutData, powersData]) => {
        this.layout = layoutData;
        this.powers = powersData;
        console.log('Layout and powers loaded.');

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

      // --- NEW: Global Socket.IO listener ---
      // This assumes you have a `socket` object initialized and connected
      // as we discussed for the editor.
      if (window.socket) {
        socket.on('power_status', (data) => {
            console.log('Received power status update:', data);

            // Find the specific widget component on the page to update it
            const widgetElement = document.getElementById(`widget-${data.id}`);
            if (widgetElement && widgetElement.__x) {
                // Call the widget's internal method to update its state
                widgetElement.__x.data.updateStatus(data.status, data.execution_id);
            }
        });
      }
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

    // addWidget(powerId) {
    //     // Check if the widget is already on the grid to prevent duplicates
    //     if (this.layout.widgets.some(w => w.power_id === powerId)) {
    //         alert('This power is already on your control grid.');
    //         return;
    //     }
    //     // Add the new widget to the layout data array
    //     this.layout.widgets.push({ power_id: powerId, position: [0,0] }); // Position will be handled by drag-and-drop
    //     console.log(`Added widget for power: ${powerId}`);
    // },

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

window.controlPanel = controlPanel;
window.Alpine = Alpine;
Alpine.start();