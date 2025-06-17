import * as Blockly from 'blockly'; // import all of blockly
import { io } from "socket.io-client";

import { pythonGenerator, Order } from 'blockly/python';

import { installMCGenerator} from "./generators/python/mc.mjs";
import { installMCMaterialsGenerator} from "./generators/python/materials.mjs";
import { installMCEntityGenerator } from "./generators/python/entities.mjs";

import {defineMineCraftBlocklyUtils} from "./lib/utils.mjs";
import {defineMineCraftConstants} from "./lib/constants.mjs";
import {defineMineCraftBlocks} from "./blocks/mc.mjs";
import {defineMineCraftMaterialBlocks} from "./blocks/materials.mjs";
import {defineMinecraftEntityBlocks} from "./blocks/entities.mjs";

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

    defineMineCraftConstants(Blockly);
    defineMineCraftBlocklyUtils(Blockly);

    defineMineCraftBlocks(Blockly);
    defineMineCraftMaterialBlocks(Blockly);
    defineMinecraftEntityBlocks(Blockly);

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
    });

    workspace.clear(); // Clear the workspace
    Blockly.serialization.workspaces.load(initialWorkspaceJson,workspace); // Load the JSON data

    // --- Attach Event Listeners for New Buttons ---
    const executeButton = document.getElementById('executePowerButton');
    if (executeButton) {
        executeButton.addEventListener('click', () => {
            // This reuses your existing logic for generating and sending code
            const code = pythonGenerator.workspaceToCode(workspace);
            const codeDisplay = document.getElementById('pythonCodeDisplay');
            if(codeDisplay) codeDisplay.value = code;

            // This would call your Flask endpoint for execution
            console.log("Executing current workspace code...");
            // fetch('/execute_power', { ... });
        });
    }

    const clearButton = document.getElementById('clearWorkspaceButton');
    if (clearButton) {
        clearButton.addEventListener('click', () => {
            workspace.clear();
            console.log("Workspace cleared.");
        });
    }

    // We will wire up New and Save buttons later when we implement saving powers.
}

// Ensure init is called after the DOM is loaded
document.addEventListener('DOMContentLoaded', init);