// src/control.js
import Alpine from 'alpinejs';
import Sortable from 'sortablejs'; // For drag-and-drop later
import 'htmx.org'; // Keep for executing powers

// The data and methods for our main control panel component
function controlPanel() {
  return {
    powers: {}, // Will hold the data for all available powers
    layout: { grid: { columns: 4 }, widgets: [] }, // Will hold the layout data
    isEditing: false, // Toggles edit mode for drag-and-drop

    init() {
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
            new Sortable(grid, {
              animation: 150,
              // More options will be added here to save the new layout
            });
          }
        });
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