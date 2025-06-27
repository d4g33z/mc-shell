// src/control.js
import Alpine from 'alpinejs';
import Sortable from 'sortablejs'; // For drag-and-drop later
import 'htmx.org'; // Keep for executing powers
// In src/control.js

/**
 * Creates the data object for a single power widget component.
 * @param {object} initialPowerData The full data for one power.
 */
function powerWidget(initialPowerData) {
    return {
        power: initialPowerData, // Store the power's data

        // You can add state specific to this widget, e.g., for its parameters
        formValues: {},

        init() {
            // Initialize form values from parameter defaults
            if (this.power && this.power.parameters) {
                this.power.parameters.forEach(param => {
                    this.formValues[param.name] = param.default;
                });
            }
        }
    };
}
// Make it globally available for the HTML to use
window.powerWidget = powerWidget;

// The data and methods for our main control panel component
function controlPanel() {
  return {
    powers: {}, // Will hold the data for all available powers
    layout: { grid: { columns: 4 }, widgets: [] }, // Will hold the layout data
    isEditing: false, // Toggles edit mode for drag-and-drop
    sortableInstance: null, // To hold our SortableJS instance

    init() {

      // --- THIS IS THE FIX for power widgets always movable---
      // 1. Watch for changes on the 'isEditing' property
      this.$watch('isEditing', (isNowEditing) => {
        if (this.sortableInstance) {
          console.log(`Setting drag-and-drop to ${isNowEditing ? 'ENABLED' : 'DISABLED'}.`);
          // 2. Enable or disable SortableJS based on the new state
          this.sortableInstance.option('disabled', !isNowEditing);
        }
      });
      // --- END OF FIX ---

      // --- THIS IS THE FIX for BUG #1 : Modal stays open---
      // Use $watch to monitor the isEditing property for changes.
      this.$watch('isEditing', (isNowEditing) => {
        console.log(`Edit mode changed to: ${isNowEditing}`);
        // If we are exiting edit mode, ensure the library modal is closed.
        if (!isNowEditing) {
          // Dispatch the event that the modal is listening for.
          window.dispatchEvent(new CustomEvent('close-library-modal'));
        }
      });
      // --- END OF FIX ---
      console.log('Initializing control panel...');
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
          const grid = this.$refs.powerGrid;
          if (grid) {
            this.sortableInstance = new Sortable(grid, {
              animation: 150,
              // More options will be added here to save the new layout
            });
            this.sortableInstance.option('disabled', true);
          }
        });
      });
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