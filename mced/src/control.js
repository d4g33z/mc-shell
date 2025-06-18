// 1. Import Alpine.js from the npm package
import Alpine from 'alpinejs';

// 2. Make Alpine available globally on the window object.
//    This is necessary so that the x-data, x-show, etc. attributes
//    in your HTML can find and interact with the Alpine library.
window.Alpine = Alpine;

// 3. Start Alpine. This tells Alpine to scan the DOM and initialize
//    all of its components (i.e., elements with x-data).
Alpine.start();

// Your other existing code, if any
console.log("MC-ED Control UI Loaded with Alpine.js from npm.");