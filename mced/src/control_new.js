// src/control.js
import Alpine from 'alpinejs';
import Sortable from 'sortablejs';
// import 'htmx.org'; // Keep for executing powers
// 1. Import all exports from the htmx.org package into a namespace variable called `htmx`.
import * as htmx from 'htmx.org';

// 2. Manually attach the imported htmx object to the global window object.
//    This makes it accessible to the hx-* attributes in your HTML.
window.htmx = htmx;

import { io } from "socket.io-client"; // <-- 1. Import the 'io' function

// --- Library Initialization ---
// import 'htmx.org';
import 'htmx-ext-json-enc';

// --- 2. Establish the Socket.IO Connection ---
const socket = io("http://localhost:5001"); // Use the address of your Python server

socket.on('connect', () => {
    console.log('Control UI connected to backend server with Socket.IO:', socket.id);
});

socket.on('disconnect', () => {
    console.log('Control UI disconnected from Socket.IO server.');
});

// --- 3. Set up a global listener for power status updates from the server ---
socket.on('power_status', (data) => {
    console.log('Received power status update:', data);
    // data should look like: {id: "power-id-abc", execution_id: "...", status: "finished"}

    // Find the specific widget on the page that this update is for.
    // The 'id' in the data corresponds to the power's ID, not the execution ID.
    const widgetElement = document.getElementById(`widget-${data.id}`);
    if (widgetElement) {
        // Dispatch a new custom event specifically on this element.
        // The widget's Alpine component will be listening for this.
        widgetElement.dispatchEvent(new CustomEvent('update-status', {
            detail: {
                status: data.status,
                executionId: data.execution_id,
                message: data.message || ''
            },
            bubbles: false // The event doesn't need to bubble
        }));
    }
});


// --- Alpine.js Component Definitions ---

function powerWidget(initialPowerData) {
    return {
        power: initialPowerData,
        formValues: {},
        status: 'Idle',
        errorMessage: '',
        currentExecutionId: null, // Track the current run
        showAdminControls: false, // Each widget tracks its own "delete button" visibility

        init() {
            // Initialize form values from parameter defaults
            if (this.power && this.power.parameters) {
                this.power.parameters.forEach(param => {
                    this.formValues[param.name] = param.default;
                });
            }
        },

        // This method is called by the widget's event listener
        updateStatus(newStatus, executionId, message = '') {
            this.status = newStatus;
            this.errorMessage = message;

            // If the power is running, store its executionId so we can cancel it
            if (newStatus === 'running') {
                this.currentExecutionId = executionId;
            }
            // If it's finished/cancelled/errored, clear the executionId
            if (['finished', 'cancelled', 'error'].includes(newStatus)) {
                this.currentExecutionId = null;
            }
        }
    };
}
window.powerWidget = powerWidget;




function controlPanel() {
  return {
    // --- STATE ---
    powers: {},
    layout: { grid: { columns: 4 }, widgets: [] },
    isEditing: false,
    sortableInstance: null,

    // --- METHODS ---
    init() {
      console.log('Initializing control panel component...');

      this.$watch('isEditing', (isNowEditing) => {

        this.updateSortableState(isNowEditing);
            window.dispatchEvent(new CustomEvent('control-mode-changed', {
            detail: { editing: isNowEditing }
        }));

      });

      // Fetch initial data
      Promise.all([
        fetch('/api/control/layout').then(res => res.json()),
        fetch('/api/powers?view=control').then(res => res.json())
      ]).then(([layoutData, powersData]) => {
        this.layout = layoutData;
        this.powers = powersData;
        console.log('Layout and power data loaded successfully.');

        // $nextTick waits for Alpine.js to finish rendering the initial widgets
        this.$nextTick(() => {
          this.initializeGrid();
        });
      });
    },

    /**
     * Initializes all functionality for the power grid, including
     * htmx event listeners and SortableJS.
     */
    initializeGrid() {
        const grid = document.getElementById('power-grid');
        if (!grid) {
            console.error("Fatal Error: Could not find #power-grid element to initialize.");
            return;
        }

        // --- THIS IS THE FIX ---
        // We attach a single, delegated listener to the grid for all htmx swaps.
        grid.addEventListener('htmx:afterSwap', (event) => {
            // event.detail.elt contains the new HTML fragment that was just added
            const newWidget = event.detail.elt;

            if (newWidget && newWidget.nodeType === Node.ELEMENT_NODE) {
                console.log('htmx:afterSwap detected on #power-grid. Initializing new widget...');

                // 1. Tell Alpine.js to initialize any x-data components inside the new widget
                window.Alpine.initTree(newWidget);

                // 2. Tell htmx to scan the new widget for any hx-* attributes
                window.htmx.process(newWidget);
            }
        });

        // Process any widgets that were loaded initially from the layout file.
        window.htmx.process(grid);

        // Initialize SortableJS
        this.sortableInstance = new Sortable(grid, {
          animation: 150,
          ghostClass: 'power-widget-ghost',
          dragClass: 'power-widget-dragging',
          onEnd: (event) => {
            // Future logic for saving the new layout order
          }
        });

        // Set the initial draggable state
        this.updateSortableState();
    },

    updateSortableState(isNowEditing) {
        if (this.sortableInstance) {
            console.log(`Setting drag-and-drop to ${isNowEditing ? 'ENABLED' : 'DISABLED'}.`);
            this.sortableInstance.option('disabled', !isNowEditing);
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

      addWidget(powerId) {
          // Check if the widget is already on the grid to prevent duplicates
          if (this.layout.widgets.some(w => w.power_id === powerId)) {
              alert('This power is already on your control grid.');
              return;
          }
          // Add the new widget to the layout data array
          this.layout.widgets.push({ power_id: powerId, position: [0,0] }); // Position will be handled by drag-and-drop
          console.log(`Added widget for power: ${powerId}`);
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
