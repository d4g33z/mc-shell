/**
 * @fileoverview Initializes global event listeners for htmx custom events.
 * This should be called once when each application page (editor, control) starts.
 */

export function initializeHtmxListeners() {
    console.log("Initializing global htmx event listeners...");

    // Listener for our custom 'showError' event sent from the Flask server
    // This handles application-specific, known error conditions.
    document.body.addEventListener('showError', function(event) {
        // The data sent from the server is available in event.detail
        console.error("Custom server error event received:", event.detail);
        const errorMessage = event.detail.errorMessage || "An unknown server error occurred.";
        alert(`Application Error: ${errorMessage}`);
    });

    // Listener for general htmx response errors (e.g., 404, 503, network failure)
    // This catches problems with the HTTP request itself.
    document.body.addEventListener('htmx:responseError', function(event) {
        console.error("HTMX Response Error:", event.detail);
        const xhr = event.detail.xhr;

        let alertMessage = `A server communication error occurred.\n\nStatus: ${xhr.status} - ${xhr.statusText}`;

        // A status of 0 often indicates a network failure (e.g., server is down, CORS issue).
        if (xhr.status === 0) {
            alertMessage = "Network Error: Could not connect to the server. Is it running?";
        }

        alert(alertMessage);
    });

    // You can add other global listeners here as well. For example,
    // showing a global loading indicator during any htmx request.
    /*
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        // e.g., document.getElementById('global-spinner').style.display = 'block';
    });
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        // e.g., document.getElementById('global-spinner').style.display = 'none';
    });
    */
}