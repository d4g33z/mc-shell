import Alpine from 'alpinejs';
import Sortable from 'sortablejs'; // For drag-and-drop later
import 'htmx.org'; // Keep for executing powers

/**
 * Creates the data object for a single power widget component.
 * It is now self-contained and listens for global state changes.
 */
function powerWidget(initialPowerData) {
    return {
        power: initialPowerData,
        formValues: {},
        showAdminControls: false, // Each widget tracks its own "delete button" visibility

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
          const grid = this.$refs.powerGrid;
          if (grid) {
            this.sortableInstance = new Sortable(grid, {
              animation: 150,

              // --- THIS IS THE DEFINITIVE FIX ---

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
              // --- END OF FIX ---



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