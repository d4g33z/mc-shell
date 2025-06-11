import * as Blockly from 'blockly'; // import all of blockly
import {blocks} from 'blockly/blocks'; // Assuming standard built-in blocks

// Merge the built-in blocks with Blockly's Blocks object.
// This step is crucial if you are not using the default blockly import
// that includes all standard blocks.
// Blockly.Blocks = {
//   ...Blockly.Blocks,
//   ...blocks
// };

import { pythonGenerator, Order } from 'blockly/python';

// test code
import { defineGreetingBlock } from './blocks/greeting.mjs'; // Import defineGreetingPython
import { installGreetingGenerator } from './generators/python/greeting.mjs'; // Import defineGreetingPython
import { installMCGenerator} from "./generators/python/mc.mjs";
import { installMCMaterialsGenerator} from "./generators/python/materials.mjs";
import { installMCEntityGenerator } from "./generators/python/entities.mjs";

import {defineMineCraftBlocklyUtils} from "./lib/utils.mjs";
import {defineMineCraftConstants} from "./lib/constants.mjs";
import {defineMineCraftBlocks} from "./blocks/mc.mjs";
import {defineMineCraftMaterialBlocks} from "./blocks/materials.mjs";
import {defineMinecraftEntityBlocks} from "./blocks/entities.mjs";

// we should have everything we need in predefined blocks
// import {defineMathBlocks} from "./blocks/math.mjs";
// import {installMathGenerators} from "./generators/python/math.mjs";

// Define the structure of a blank workspace
const BLANK_WORKSPACE_JSON = {
  "blocks": {
    "languageVersion": 0,
    "blocks": [] // An empty array of blocks
  },
  "variables": [] // An empty array of variables
};

import defaultWorkspaceJson from './workspace.json';
const AUTOSAVE_KEY = 'blocklyMinecraftAutosave'; // Key for localStorage

// Global workspace variable so it's accessible by save/load functions
// let workspace;

// At the top of src/index.js
import { io } from "socket.io-client";

// --- Connect to the WebSocket server ---
// The { transports: ['websocket'] } part can help avoid some connection issues.
const socket = io("http://localhost:5001", { transports: ['websocket'] });

socket.on('connect', () => {
    console.log('Connected to backend server with Socket.IO:', socket.id);
});

// Listen for status updates from the server
socket.on('power_status', (data) => {
    console.log('Received power status update:', data);
    // Find the UI element for this power and update its status
    const powerElement = document.getElementById(`power-${data.id}`);
    if (powerElement) {
        const statusSpan = powerElement.querySelector('.status');
        statusSpan.textContent = `Status: ${data.status}`;
        if (data.status === 'finished' || data.status === 'error' || data.status === 'cancelled') {
            // Re-enable execute button, remove cancel button
            powerElement.querySelector('.execute-btn').disabled = false;
            const cancelButton = powerElement.querySelector('.cancel-btn');
            if (cancelButton) cancelButton.remove();
        }
        if(data.status === 'error') {
            statusSpan.textContent += ` - ${data.message}`;
            statusSpan.style.color = 'red';
        }
    }
});
async function init() {

    // defineMathBlocks(Blockly);

    defineMineCraftBlocklyUtils(Blockly);
    defineMineCraftConstants(Blockly);
    defineMineCraftBlocks(Blockly);
    defineMineCraftMaterialBlocks(Blockly);
    defineMinecraftEntityBlocks(Blockly);

    defineGreetingBlock(Blockly)
    installGreetingGenerator(pythonGenerator);
    installMCGenerator(pythonGenerator,Order);
    installMCMaterialsGenerator(pythonGenerator)
    installMCEntityGenerator(pythonGenerator)

    // Attempt to load autosaved workspace, otherwise use default
    const initialWorkspaceJson = loadAutosavedWorkspace();

    var workspace = Blockly.inject('blocklyDiv', {
        toolbox: document.getElementById('toolbox'),
        grid: {
            spacing: 20,
            length: 3,
            colour: '#ccc',
            snap: true
        },
        zoom: {
            controls: true,
            wheel: true,
            startScale: 1.0,
            maxScale: 3,
            minScale: 0.3,
            scaleSpeed: 1.2
        },
        json: initialWorkspaceJson
    });
    // --- Setup Autosave on Page Unload/Reload ---
    window.addEventListener('beforeunload', function (e) {
        autosaveWorkspace();
        // Standard way to try and show a confirmation dialog (browser support varies)
        // e.preventDefault(); // If you want to try to prevent immediate close
        // e.returnValue = ''; // Necessary for some browsers
    });

    workspace.clear(); // Clear the workspace
    Blockly.serialization.workspaces.load(initialWorkspaceJson,workspace); // Load the JSON data

    // window.saveWorkspaceToJson = function () {
    //     // 1. Serialize workspace to JSON object
    //     const workspaceJson = Blockly.serialization.workspaces.save(workspace);
    //
    //     // 2. Convert JSON object to a JSON string
    //     const jsonText = JSON.stringify(workspaceJson, null, 2); // Use null, 2 for pretty printing
    //
    //     // 3. Create a download link for the JSON file
    //     const filename = 'workspace.json'; // Updated filename extension
    //
    //     const element = document.createElement('a');
    //     element.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(jsonText)); // Updated MIME type
    //     element.setAttribute('download', filename);
    //
    //     element.style.display = 'none';
    //     document.body.appendChild(element);
    //
    //     element.click();
    //
    //     document.body.removeChild(element);
    // }

    function clearPythonCodeDisplay() {
        // 1. Find the textarea element in the document by its ID.
        const codeTextarea = document.getElementById('pythonCodeDisplay');

        // 2. Check if the element was found to avoid errors.
        if (codeTextarea) {
            // 3. Set the 'value' property of the textarea to an empty string.
            codeTextarea.value = '';
        } else {
            // Log an error to the console if the element couldn't be found.
            console.error("Error: Could not find the textarea with ID 'pythonCodeDisplay'.");
        }
    }

    window.clearWorkspace = function () {
        workspace.clear();
        clearPythonCodeDisplay();
    }
// --- Function to Save Workspace to localStorage ---
    window.autosaveWorkspace = function () {
        if (workspace) {
            try {
                const workspaceJson = Blockly.serialization.workspaces.save(workspace);
                const jsonText = JSON.stringify(workspaceJson);
                localStorage.setItem(AUTOSAVE_KEY, jsonText);
                console.log('Workspace autosaved to localStorage.');
            } catch (e) {
                console.error('Error autosaving workspace:', e);
            }
        }
    }

// --- Function to Load Workspace from localStorage ---
    function loadAutosavedWorkspace () {
        try {
            const savedJsonText = localStorage.getItem(AUTOSAVE_KEY);
            if (savedJsonText) {
                const loadedWorkspaceJson = JSON.parse(savedJsonText);
                // Check if the loaded JSON is valid and has blocks
                if (loadedWorkspaceJson && loadedWorkspaceJson.blocks && loadedWorkspaceJson.blocks.blocks && loadedWorkspaceJson.blocks.blocks.length > 0) {
                    console.log('Found autosaved workspace. Loading it.');
                    return loadedWorkspaceJson; // Return the loaded JSON
                } else {
                    console.log('Autosaved workspace is empty or invalid. Loading default.');
                }
            } else {
                console.log('No autosaved workspace found. Loading default.');
            }
        } catch (e) {
            console.error('Error loading autosaved workspace:', e);
            // Fallback to default if there's an error
        }
        return defaultWorkspaceJson; // Fallback to your predefined default
    }

    window.saveWorkspaceToJson =  async function () { // Make the function async
        try {
            // 1. Serialize workspace to JSON object
            const workspaceJson = Blockly.serialization.workspaces.save(workspace); // Assuming 'workspace' is your Blockly workspace instance

            // 2. Convert JSON object to a JSON string
            const jsonText = JSON.stringify(workspaceJson, null, 2); // Pretty printing

            // 3. Define suggested filename and accepted file types
            const suggestedName = 'workspace.json';
            const fileTypes = [
                {
                    description: 'JSON Files',
                    accept: {
                        'application/json': ['.json'],
                    },
                },
            ];

            // 4. Check if the API is available
            if (window.showSaveFilePicker) {
                // Show the "Save As" dialog
                const fileHandle = await window.showSaveFilePicker({
                    suggestedName: suggestedName,
                    types: fileTypes,
                });

                // Create a writable stream
                const writableStream = await fileHandle.createWritable();

                // Write the JSON content to the file
                await writableStream.write(jsonText);

                // Close the file and write the contents to disk
                await writableStream.close();

                console.log('Workspace saved successfully to:', fileHandle.name);

            } else {
                // Fallback for browsers that don't support showSaveFilePicker()
                // (This is your original download link method)
                console.warn('showSaveFilePicker API not supported. Falling back to direct download.');
                const filename = suggestedName;
                const element = document.createElement('a');
                element.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(jsonText));
                element.setAttribute('download', filename);
                element.style.display = 'none';
                document.body.appendChild(element);
                element.click();
                document.body.removeChild(element);
            }
        } catch (error) {
            // Handle errors, e.g., if the user cancels the dialog
            if (error.name === 'AbortError') {
                console.log('Save dialog was cancelled by the user.');
            } else {
                console.error('Error saving workspace:', error);
            }
        }
    };
    // --- Function to Load Workspace from a User-Selected JSON File ---
    window.loadWorkspaceFromJson = async function () {
        if (!workspace) {
            console.error("Blockly workspace is not initialized yet.");
            alert("Workspace not ready. Please wait a moment and try again.");
            return;
        }

        try {
            // 1. Use File System Access API if available
            if (window.showOpenFilePicker) {
                const [fileHandle] = await window.showOpenFilePicker({
                    types: [
                        {
                            description: 'Blockly Workspace JSON',
                            accept: {
                                'application/json': ['.json'],
                            },
                        },
                    ],
                    multiple: false, // Only allow selecting one file
                });

                const file = await fileHandle.getFile();
                const jsonText = await file.text();
                const loadedWorkspaceJson = JSON.parse(jsonText);

                // Clear the current workspace BEFORE loading new data
                workspace.clear();
                Blockly.serialization.workspaces.load(loadedWorkspaceJson, workspace);

                console.log('Workspace loaded successfully from:', fileHandle.name);
                autosaveWorkspace(); // Optionally autosave after a successful manual load

            } else {
                // Fallback for older browsers (using a hidden file input element)
                console.warn('showOpenFilePicker API not supported. Using file input fallback.');
                const inputElement = document.createElement('input');
                inputElement.type = 'file';
                inputElement.accept = '.json,application/json'; // Filter for JSON files

                inputElement.onchange = async (event) => {
                    const file = event.target.files[0];
                    if (file) {
                        const jsonText = await file.text();
                        try {
                            const loadedWorkspaceJson = JSON.parse(jsonText);

                            workspace.clear();
                            Blockly.serialization.workspaces.load(loadedWorkspaceJson, workspace);

                            console.log('Workspace loaded successfully from:', file.name);
                            autosaveWorkspace(); // Optionally autosave
                        } catch (e) {
                            console.error('Error parsing or loading workspace JSON from file input:', e);
                            alert('Error loading workspace: Invalid JSON file.');
                        }
                    }
                };
                inputElement.click(); // Programmatically click the hidden input to open the dialog
            }
        } catch (error) {
            // Handle errors, e.g., if the user cancels the dialog
            if (error.name === 'AbortError') {
                console.log('File open dialog was cancelled by the user.');
            } else {
                console.error('Error opening or loading workspace from file:', error);
                alert('Error opening file.');
            }
        }
    }

    // This function is attached to your "Generate Python" button's click handler
    window.generatePythonCode = function () {
        if (!workspace) {
            console.error("Workspace is not ready.");
            return;
        }

        // --- FIX: Initialize the generator before generating code ---
        // This resets the state, including the name database (nameDB_).
        pythonGenerator.init(workspace);

        // Now, this call will work correctly.
        const pythonCode = pythonGenerator.workspaceToCode(workspace);

        const codeTextarea = document.getElementById('pythonCodeDisplay');
        if (codeTextarea) {
            codeTextarea.value = pythonCode; // Set textarea value
        } else {
            console.warn("Textarea with id 'pythonCodeDisplay' not found.");
        }
    };

    async function executeIPythonCommand(command, commandArguments) {
        const apiEndpoint = 'http://localhost:5000/ipython_magic'; // API server URL
        const requestData = {command: command, arguments: commandArguments};

        try {
            const response = await fetch(apiEndpoint, {
                method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.error) {
                console.error("IPython Magic Error:", data.error);
                alert(`IPython Command Error: ${data.error}`); // Or better error handling in UI
                return null;
            } else {
                console.log("IPython Magic Output:", data.output);
                return data.output; // Process and display the output in your editor
            }

        } catch (error) {
            console.error("Fetch error calling IPython API:", error);
            alert("Error communicating with IPython process."); // User-friendly error
            return null;
        }
    }

// Example of calling this function when a button is clicked or a Blockly event occurs:
    window.callPythonFromBlockly = async function () { // Example - make it global for button onClick
        console.log("Inside callPythonFromBlockly")
        const commandToExecute = '%ls'; // Example magic command - list files
        const commandArgs = '-l . ';   // Example arguments
        const output = await executeIPythonCommand(commandToExecute, commandArgs);
        // if (output) {
        //     document.getElementById('pythonCodeDisplay').value = "IPython Output:\n" + output; // Display output
        // }
    };

    window.createPythonScript = async function () { // Example - make it global for button onClick
        console.log("Inside executePythonCode")
        generatePythonCode() // generate what is visible in text area
        const commandToExecute = '%mc_create_script'; // Example magic command - list files
        const commandArgs = document.getElementById('pythonCodeDisplay').value;   // Example arguments
        const output = await executeIPythonCommand(commandToExecute, commandArgs);
        // if (output) {
        //     document.getElementById('pythonCodeDisplay').value = "IPython Output:\n" + output; // Display output
        // }
    };

    window.createPower = async function() {
            autosaveWorkspace();
            const code = pythonGenerator.workspaceToCode(workspace);

            // For now, let's just add the generated code as a new "power" in the UI
            addPowerToList(code, `Power_${new Date().getTime()}`);
    }

    window.addPowerToList = function (pythonCode, powerName) {
        const powerListDiv = document.getElementById('powerList'); // Assumes you have <div id="powerList"></div> in your HTML
        if (!powerListDiv) return;

        const powerId = `temp-id-${Math.random()}`; // Temporary ID until executed
        const powerElement = document.createElement('div');
        powerElement.className = 'power-item';
        powerElement.id = `power-${powerId}`;
        powerElement.dataset.code = pythonCode; // Store the code on the element

        powerElement.innerHTML = `
            <span class="power-name">${powerName}</span>
            <span class="status">Status: Saved</span>
            <button class="execute-btn">Execute</button>
        `;

        powerListDiv.appendChild(powerElement);

        // Add event listener for the new execute button
        powerElement.querySelector('.execute-btn').addEventListener('click', async (event) => {
            const button = event.target;
            button.disabled = true; // Prevent multiple clicks

            const powerDiv = button.closest('.power-item');
            const codeToRun = powerDiv.dataset.code;
            const statusSpan = powerDiv.querySelector('.status');
            statusSpan.textContent = 'Status: Dispatching...';
            statusSpan.style.color = 'orange';

            const playerSelector = document.getElementById('playerSelector');
            const selectedPlayer = playerSelector.value;

            try {
                const response = await fetch('/execute_power', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: codeToRun, playerName: selectedPlayer }), // Send code
                });
                const result = await response.json();

                if (result.power_id) {
                    // Update the element's ID to the real one from the server
                    powerDiv.id = `power-${result.power_id}`;
                    // Add a cancel button
                    const cancelButton = document.createElement('button');
                    cancelButton.className = 'cancel-btn';
                    cancelButton.textContent = 'Cancel';
                    cancelButton.onclick = () => cancelPower(result.power_id);
                    powerDiv.appendChild(cancelButton);
                }
            } catch (error) {
                console.error('Error dispatching power:', error);
                statusSpan.textContent = 'Status: Dispatch Error';
                statusSpan.style.color = 'red';
                button.disabled = false;
            }
        });
    }

    async function cancelPower(powerId) {
        console.log(`Requesting cancellation for ${powerId}`);
        try {
            await fetch('/cancel_power', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ power_id: powerId }),
            });
        } catch (error) {
            console.error('Error sending cancellation request:', error);
        }
    }
}

init();