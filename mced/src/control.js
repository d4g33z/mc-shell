// --- Import and initialize libraries for the control page ---
import Alpine from 'alpinejs';
import 'htmx.org';

// --- NEW: Import and call the htmx listener initializer ---
import { initializeHtmxListeners } from './lib/htmx_listeners.js';

window.Alpine = Alpine;
Alpine.start();

// Call the initializer function to set up error handling for this page
initializeHtmxListeners();

console.log("MC-ED Control UI Loaded with shared htmx listeners.");