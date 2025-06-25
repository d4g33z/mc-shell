// src/control.js

// --- Library Initialization ---
import Alpine from 'alpinejs';
import 'htmx.org';
import 'htmx-ext-json-enc'; // Good to include this for future use

// Make Alpine globally available for the x-data attributes in the HTML
window.Alpine = Alpine;

// Start Alpine to initialize components on this page
Alpine.start();

console.log("MC-ED Control UI Initialized.");

// This file will later contain logic for SortableJS, etc.