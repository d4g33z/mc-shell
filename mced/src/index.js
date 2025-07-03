import Alpine from 'alpinejs';
import 'htmx.org'; // Imports for its side effect of initializing on the window
import 'htmx-ext-json-enc'; // Imports the extension
import Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/themes/prism-okaidia.css';

import * as Blockly from 'blockly';
import { pythonGenerator } from 'blockly/python';
import { defineMineCraftBlocks } from "./blocks/mc.mjs";
import { defineMineCraftMaterialBlocks } from "./blocks/materials.mjs";
import { defineMinecraftEntityBlocks } from "./blocks/entities.mjs";
import {defineMineCraftConstants, MCED} from "./lib/constants.mjs";
import { defineMineCraftBlocklyUtils } from "./lib/utils.mjs";
import { installMCGenerator } from "./generators/python/mc.mjs"
import { installMCMaterialsGenerator } from "./generators/python/materials.mjs";
import { installMCEntityGenerator } from "./generators/python/entities.mjs";
import { initializeHtmxListeners } from './lib/htmx_listeners.js';

// --- Global Setup ---

// Make Alpine globally available BEFORE it starts.
// This is necessary for the x-data attributes in the HTML to find it.
window.Alpine = Alpine;

// Define the structure for a completely empty workspace
const BLANK_WORKSPACE_JSON = {
    "blocks": { "languageVersion": 0, "blocks": [] },
    "variables": []
};

// Use a constant for the localStorage key to avoid typos
const AUTOSAVE_KEY = 'mcEdWorkspaceAutosave';

// A module-scoped variable to hold the main workspace instance
let workspace;

// Add this helper function somewhere accessible, e.g., near the top of index.js
/**
 * Escapes characters in a string that have a special meaning in regular expressions.
 * @param {string} str The string to escape.
 * @returns {string} The escaped string.
 */
function escapeRegExp(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}

async function handleDeletePower(powerId) {
    if (!powerId) return;

    console.log(`Sending request to delete power: ${powerId}`);
    try {
        const response = await fetch(`/api/power/${powerId}`, {
            method: 'DELETE',
        });

        // The htmx part of the response now handles the refresh.
        // We just need to check if the call was successful.
        if (response.ok) {
            console.log("Delete request successful. The server will trigger a library refresh.");
            // No need to manually remove the element from the DOM!
            // The HX-Trigger header from the server will cause the #power-list to reload.
            window.dispatchEvent(new CustomEvent('library-changed', { bubbles: true }));
        } else {
            const errorText = await response.text();
            console.error('Error deleting power:', response.status, errorText);
            alert(`Failed to delete power: ${errorText}`);
        }
    } catch (error) {
        console.error('Network error while deleting power:', error);
        alert('Network error. Could not delete power.');
    }
}

window.handleDeletePower = handleDeletePower;

// --- Main Application Logic ---
async function init() {

    /**
     * Sends a command and its arguments to the Flask server's IPython endpoint.
     * @param {string} command The magic command to run (e.g., '%mc_create_script').
     * @param {string} commandArguments The string of arguments for the command.
     * @returns {Promise<string|null>} The output from the command or null on error.
    */
    async function executeIPythonCommand(command, commandArguments) {
        const apiEndpoint = '/api/ipython_magic'; // We can use a relative path thanks to the proxy
        const requestData = { command: command, arguments: commandArguments };

        try {
            const response = await fetch(apiEndpoint, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.error) {
                console.error("IPython Magic Error:", data.error);
                alert(`IPython Command Error: ${data.error}`);
                return null;
            } else {
                console.log("IPython Magic Output:", data.output);
                return data.output;
            }

        } catch (error) {
            console.error("Fetch error calling IPython API:", error);
            alert("Error communicating with IPython process.");
            return null;
        }
    }

    /**
    * Handles opening a file picker and loading a workspace from a JSON file.
    */
    async function handleLoadPowerFromFile() {
        if (!workspace) {
            alert("Workspace is not ready yet.");
            return;
        }

        // Modern browsers support the File System Access API
        if (window.showOpenFilePicker) {
            try {
                // 1. Show the native "Open File" dialog
                const [fileHandle] = await window.showOpenFilePicker({
                    types: [{
                        description: 'Blockly Workspace Files',
                        accept: { 'application/json': ['.json'] },
                    }],
                    multiple: false,
                });

                // 2. Get the file content
                const file = await fileHandle.getFile();
                const jsonText = await file.text();
                const loadedJson = JSON.parse(jsonText);

                // 3. Load the content into Blockly
                workspace.clear(); // Clear the existing blocks
                Blockly.serialization.workspaces.load(loadedJson, workspace);
                console.log(`Successfully loaded power from: ${file.name}`);

            } catch (error) {
                // This error is commonly thrown if the user clicks "Cancel" in the file dialog.
                if (error.name === 'AbortError') {
                    console.log('User cancelled the file open dialog.');
                } else {
                    console.error('Error opening or loading file:', error);
                    alert('An error occurred while trying to load the file.');
                }
            }
        } else {
            // Fallback for older browsers
            console.warn('File System Access API not supported. Using legacy file input.');
            const inputElement = document.createElement('input');
            inputElement.type = 'file';
            inputElement.accept = '.json,application/json';

            inputElement.onchange = async (event) => {
                const file = event.target.files[0];
                if (file) {
                    try {
                        const jsonText = await file.text();
                        const loadedJson = JSON.parse(jsonText);

                        workspace.clear();
                        Blockly.serialization.workspaces.load(loadedJson, workspace);
                        console.log(`Successfully loaded power from: ${file.name}`);
                    } catch (e) {
                        console.error('Error parsing or loading file:', e);
                        alert('Error loading workspace: The selected file is not valid JSON.');
                    }
                }
            };
            inputElement.click();
        }
    }

    /**
     * Saves the current Blockly workspace state to the browser's localStorage.
     */
    function autosaveWorkspace() {
        if (!workspace) {
            return; // Do nothing if the workspace isn't initialized yet
        }
        try {
            // Serialize the workspace to a JSON object
            const workspaceJson = Blockly.serialization.workspaces.save(workspace);
            // Convert the object to a string to store it
            const jsonText = JSON.stringify(workspaceJson);
            // Save it to localStorage
            localStorage.setItem(AUTOSAVE_KEY, jsonText);
            console.log('Workspace autosaved to localStorage.');
        } catch (e) {
            console.error('Error during autosave:', e);
        }
    }


    /**
     * Attempts to load a workspace from localStorage.
     * If no valid autosave is found, it returns the provided default JSON.
     * @param {object} defaultJson The default workspace JSON to use as a fallback.
     * @return {object} The workspace JSON to load.
     */
    function loadAutosavedWorkspace(defaultJson) {
        try {
            const savedJsonText = localStorage.getItem(AUTOSAVE_KEY);
            if (savedJsonText) {
                const loadedJson = JSON.parse(savedJsonText);
                // Basic validation to make sure we're loading a real workspace
                if (loadedJson && loadedJson.blocks) {
                    console.log('Found and loaded workspace from localStorage.');
                    return loadedJson;
                }
            }
        } catch (e) {
            console.error('Error loading autosaved workspace:', e);
            // If there's an error, we'll fall back to the default
        }
        // If no valid autosave was found, return the default
        console.log('No valid autosave found, loading default workspace.');
        return defaultJson;
    }

    // TODO: these helpers can be defined externally and attached to window to make available here
    /**
     * A helper function that takes a function and returns a new version of it
     * that will only run after a specified delay of inactivity.
     * @param {Function} func The function to debounce.
     * @param {number} timeout The delay in milliseconds.
     * @return {Function} The new debounced function.
     */
    function debounce(func, timeout = 500) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => { func.apply(this, args); }, timeout);
        };
    }

    /**
     * Gathers data from the editor modal and the Blockly workspace,
     * then POSTs the complete "Power Object" to the server.
     *
     * The definitive save function. It enforces the "Debug-to-Define" pattern.
     * When saving a functional power, it requires a corresponding call block with
     * all arguments connected to exist on the workspace. It uses these connections
     * to authoritatively determine the parameter types.
     */
    async function handleSavePower() {
        console.log("Handling save power with strict type introspection...");

        // 1. Get metadata from the modal form
        const formElement = document.getElementById('savePowerForm');
        if (!formElement) return;
        const formData = new FormData(formElement);
        const formDataObject = Object.fromEntries(formData.entries());

        if (!formDataObject.name) {
            alert("Please enter a name for your power.");
            return;
        }

        // 2. Initialize data objects
        const blocklyJson = Blockly.serialization.workspaces.save(workspace);
        let powerParameters = [];
        let powerFunctionName = null;
        let codeToSave = null;

        // 3. Find the function definition block
        const topBlocks = workspace.getTopBlocks(true);
        const funcDefBlock = topBlocks.find(b =>
            b.type === 'procedures_defnoreturn' || b.type === 'procedures_defreturn'
        );

        if (funcDefBlock) {
            // --- This is a "Functional Power" ---
            powerFunctionName = funcDefBlock.getFieldValue('NAME');
            console.log(`Found functional power definition: '${powerFunctionName}'.`);

            // --- THIS IS THE FIX ---
            // Manually construct the Python code for the function definition.
            const funcNameForCode = pythonGenerator.nameDB_.getName(powerFunctionName, MCED.BlocklyNameTypes.PROCEDURE);
            const argNames = funcDefBlock.getVars();
            const argsForDef = argNames.map(name => pythonGenerator.nameDB_.getName(name, MCED.BlocklyNameTypes.VARIABLE));

            let funcBody = pythonGenerator.statementToCode(funcDefBlock, 'STACK') || (pythonGenerator.INDENT + 'pass\n');

            if (funcDefBlock.type === 'procedures_defreturn') {
                const returnValue = pythonGenerator.valueToCode(funcDefBlock, 'RETURN', pythonGenerator.ORDER_NONE) || 'None';
                funcBody += pythonGenerator.INDENT + 'return ' + returnValue + '\n';
            }

            codeToSave = `def ${funcNameForCode}(self, ${argsForDef.join(', ')}):\n${funcBody}`;
            // --- END OF FIX ---

            // 4. Find the corresponding call block. It is now mandatory.
            const funcCallBlock = topBlocks.find(b =>
                (b.type === 'procedures_callnoreturn' || b.type === 'procedures_callreturn') &&
                b.getFieldValue('NAME') === powerFunctionName
            );

            if (!funcCallBlock) {
                alert(`Save Error: To save the function '${powerFunctionName}', you must place a "call ${powerFunctionName}" block on the workspace to define its parameter types.`);
                return;
            }

            // 5. Extract parameter names and types from the call block's inputs.
            // const argNames = funcDefBlock.getVars();
            if (argNames.length > 0) {
                for (let i = 0; i < argNames.length; i++) {
                    const argName = argNames[i];
                    let extractedType = null; // Start with null

                    const input = funcCallBlock.getInput('ARG' + i);
                    if (!input || !input.connection || !input.connection.targetBlock()) {
                        // This input is empty. Abort the save.
                        alert(`Save Error for function '${powerFunctionName}': The parameter '${argName}' must have a block connected to it to define its type.`);
                        return; // Stop the entire save process
                    }

                    // A block is connected, so we can get its type.
                    const connectedBlock = input.connection.targetBlock();
                    const outputConnection = connectedBlock.outputConnection;

                    if (outputConnection && outputConnection.getCheck()) {
                        const checks = outputConnection.getCheck();
                        if (checks && checks.length > 0) {
                            extractedType = checks[0]; // e.g., "Number", "Block", "3DVector"
                        }
                    }

                    if (!extractedType) {
                         alert(`Save Error for function '${powerFunctionName}': Could not determine the type for parameter '${argName}'. Please ensure the connected block has an output type.`);
                         return;
                    }

                    console.log(`- Found parameter: '${argName}' of type '${extractedType}'`);
                    powerParameters.push({
                        name: argName,
                        type: extractedType,
                        default: 0 // Default value can be refined later
                    });
                }
            }

        } else {
            // --- This is a "Script Power" ---
            console.log("No function definition found. Saving as a 'Script Power'.");
            codeToSave = pythonGenerator.workspaceToCode(workspace);
        }

        // --- NEW: Dependency Analysis ---
        const dependencies = [];
        // getDescendants() returns the function block and all blocks inside it
        const allChildBlocks = funcDefBlock.getDescendants(false);

        for (const childBlock of allChildBlocks) {
            // We are looking for blocks that call another function
            if (childBlock.type === 'procedures_callnoreturn' || childBlock.type === 'procedures_callreturn') {
                const calledFunctionName = childBlock.getFieldValue('NAME');
                if (calledFunctionName && !dependencies.includes(calledFunctionName)) {
                    dependencies.push(calledFunctionName);
                }
            }
        }
        console.log(`Found dependencies: ${dependencies.join(', ')}`);
        // --- END OF NEW LOGIC ---

        // 6. Assemble and POST the final Power Object
        const powerDataObject = {
            name: formDataObject.name,
            description: formDataObject.description,
            category: formDataObject.category || "General",
            power_id: formDataObject.power_id || null,
            function_name: powerFunctionName,
            parameters: powerParameters,
            blockly_json: blocklyJson,
            python_code: codeToSave,
            dependencies: dependencies // <-- Save the new dependency list
        };

        console.log("Sending final power data to server:", powerDataObject);

        try {
            const response = await fetch('/api/powers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(powerDataObject),
            });

            if (response.ok) {
                alert(`Power "${formDataObject.name}" saved successfully!`);
                window.dispatchEvent(new CustomEvent('library-changed'));
            } else {
                alert(`Failed to save power: ${await response.text()}`);
            }
        } catch (error) {
            console.error('Network error while saving power:', error);
            alert('Network error. Could not save power.');
        }
    }
    // --- 1. Define all custom elements in the correct order ---
    // Utilities and custom fields must be defined first.
    defineMineCraftBlocklyUtils(Blockly);
    // Constants populates Blockly.Msg and MCED.Defaults used by other blocks.
    defineMineCraftConstants(Blockly);
    // Now define all block types.
    defineMineCraftBlocks(Blockly);
    defineMineCraftMaterialBlocks(Blockly);
    defineMinecraftEntityBlocks(Blockly);

    // --- 2. Install all Python generators ---

    installMCGenerator(pythonGenerator);
    installMCMaterialsGenerator(pythonGenerator);
    installMCEntityGenerator(pythonGenerator);

    // --- Determine the initial workspace to load ---
    // It will prioritize localStorage, then workspace.json, then a blank slate.
    // (This re-uses the fetch logic from our previous discussion)
    let initialWorkspaceJson = loadAutosavedWorkspace(null); // Try localStorage first


    if (!initialWorkspaceJson) {
        try {
            const response = await fetch('./workspace.json'); // Path relative to index.html
            if (response.ok) {
                initialWorkspaceJson = await response.json();
            } else {
                initialWorkspaceJson = BLANK_WORKSPACE_JSON;
            }
        } catch (e) {
            initialWorkspaceJson = BLANK_WORKSPACE_JSON;
        }
    }

    // --- ADD THIS LINE FOR DEBUGGING ---
    console.log("Workspace will be initialized with this JSON:", initialWorkspaceJson);
    // For a more readable, indented view, you can use JSON.stringify:
    // console.log("Workspace will be initialized with this JSON:", JSON.stringify(initialWorkspaceJson, null, 2));
    // ------

    // --- 3. Define the complete Toolbox ---
     // --- NEW: Fetch the toolbox from the external file ---

    // 1. Create a URL object pointing to your static asset.
    //    `import.meta.url` is a standard way to get the current module's location.
    //    Parcel understands this and will correctly process 'toolbox.xml'.
    const toolboxUrl = new URL('./toolbox.xml', import.meta.url);

    // 2. Fetch the toolbox from the URL provided by Parcel.
    let toolboxXml;
    try {
        const response = await fetch(toolboxUrl); // Use the URL object directly
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        toolboxXml= await response.text();
    } catch (error) {
        console.error("Could not load toolbox.xml. Using empty toolbox.", error);
        toolboxXml= '<xml></xml>'; // Provide a safe fallback
    }

    // --- 4. Inject Blockly into the page ---
    // For now, we start with a blank workspace.
    // Later, this could load from an autosave or a default file.
    workspace = Blockly.inject('blocklyDiv', {
        toolbox: toolboxXml,
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
    });

    initializeHtmxListeners();

    // 2. Now that the workspace exists, programmatically load the JSON data.
    //    This is more reliable as it happens after the initial render.
    if (initialWorkspaceJson && initialWorkspaceJson.blocks) {
        try {
            // No need to clear, as the workspace is fresh. But if this logic were
            // used in a "Load" function, workspace.clear() would come first.
            Blockly.serialization.workspaces.load(initialWorkspaceJson, workspace);
            console.log("Successfully loaded initial workspace from JSON data.");
        } catch (e) {
            console.error("Error loading workspace JSON data:", e);
            // In case of error, the user is left with a blank workspace.
        }
    }

    // --- 3. Set up the autosave triggers ---
    console.log("Setting up autosave listeners.");
    // Save when the user is about to leave or reload the page
    window.addEventListener('beforeunload', autosaveWorkspace);


    // --- 4. (IMPROVEMENT) Also save periodically after changes ---
    const debouncedAutosave = debounce(autosaveWorkspace, 1000); // Wait 1 second after changes
    workspace.addChangeListener((event) => {
        if (event.isUiEvent) return; // Don't save on clicks, scrolls, etc.
        debouncedAutosave();
    });

    // // --- 5. Update the "Clear Workspace" button ---
    const clearWorkspaceButton = document.getElementById('clearWorkspaceButton');

    if (clearWorkspaceButton) {
        clearWorkspaceButton.addEventListener('click', () => {
            if (confirm("Are you sure you want to clear the workspace? This cannot be undone.")) {
                workspace.clear();
                // Crucially, remove the autosaved data as well
                localStorage.removeItem(AUTOSAVE_KEY);
                console.log("Workspace and autosave data cleared.");
            }
        });
    }
    // --- LIVE GENERATION & HIGHLIGHTING LOGIC ---

    // Get a reference to the <code> element where code will be displayed
    const codeDisplayElement = document.getElementById('pythonCodeDisplay');

    // Create a debounced version of our update function
    const debouncedCodeUpdate = debounce(() => {
        if (!workspace || !pythonGenerator) return; // Safety check

        // Generate the Python code from the current workspace
        const code = pythonGenerator.workspaceToCode(workspace);

        if (codeDisplayElement) {
            // Update the text content of the <code> element
            codeDisplayElement.textContent = code;

            // Tell Prism to re-highlight the element
            // window.Prism is correct because Prism attaches itself to the global window object
            if (window.Prism) {
                Prism.highlightElement(codeDisplayElement);
            }
        }
    });

    // Add a listener to the workspace.
    workspace.addChangeListener((event) => {
        // Don't re-render for UI events like selecting a block or scrolling
        if (event.isUiEvent) {
            return;
        }
        debouncedCodeUpdate();
    });


    // Trigger an initial generation to populate the view on load
    debouncedCodeUpdate();

    // --- Wire up the "Delete" button inside the modal ---
    // const confirmDeleteButton = document.getElementById('confirmDeleteButton');
    // if (confirmDeleteButton) {
    //     console.log("inside confirmDeleteButton");
    //     confirmDeleteButton.addEventListener('click', handleDeletePower);
    // }

    // --- Wire up the "Save to Library" button inside the modal ---
    const confirmSaveButton = document.getElementById('confirmSaveButton');
    if (confirmSaveButton) {
        confirmSaveButton.addEventListener('click', handleSavePower);
    }

    // Attach the load function to the new button
    const loadButton = document.getElementById('loadPowerFromFileButton');
    if (loadButton) {
        loadButton.addEventListener('click', handleLoadPowerFromFile);
    }


    /**
     * The definitive payload builder for the "Execute (Debug)" button.
     * It inspects the workspace to determine if it's a single "functional power"
     * or a general "script power". It then extracts the correct code, parameter
     * types (from the test harness), and debug values.
     * * @param {Blockly.Workspace} workspace The Blockly workspace instance.
     * @returns {object|null} An object containing the payload for the server, or null if the
     * required blocks for a debug run aren't found.
     */
    function buildDebugPayload(workspace) {
        // We MUST initialize the generator to clear the state from any previous run.
        pythonGenerator.init(workspace);

        const topBlocks = workspace.getTopBlocks(true);

        // --- Check if the workspace represents a "Functional Power" ---
        // A functional power has a function definition and a corresponding call block.
        const funcDefBlock = topBlocks.find(b =>
            b.type === 'procedures_defnoreturn' || b.type === 'procedures_defreturn'
        );

        if (funcDefBlock) {
            const functionName = funcDefBlock.getFieldValue('NAME');

            // The "Debug-to-Define" pattern requires a corresponding call block to exist.
            const funcCallBlock = topBlocks.find(b =>
                (b.type === 'procedures_callnoreturn' || b.type === 'procedures_callreturn') &&
                b.getFieldValue('NAME') === functionName
            );

            if (!funcCallBlock) {
                alert(`Debug Error: To test the function '${functionName}', you must have a corresponding "call ${functionName}" block on the workspace with its arguments connected.`);
                return null;
            }

            console.log(`Building debug payload for functional power: '${functionName}'`);

            // --- Assemble the Payload for a Functional Power ---

            // 1. Get the pure Python code for ONLY the function definition.
            //    This part was failing before. We manually construct it now.
            const funcNameForCode = pythonGenerator.nameDB_.getName(functionName, MCED.BlocklyNameTypes.PROCEDURE);
            const argNames = funcDefBlock.getVars();
            const argsForDef = argNames.map(name => pythonGenerator.nameDB_.getName(name, MCED.BlocklyNameTypes.VARIABLE));
            let funcBody = pythonGenerator.statementToCode(funcDefBlock, 'STACK') || (pythonGenerator.INDENT + 'pass\n');
            if (funcDefBlock.type === 'procedures_defreturn') {
                const returnValue = pythonGenerator.valueToCode(funcDefBlock, 'RETURN', pythonGenerator.ORDER_NONE) || 'None';
                funcBody += pythonGenerator.INDENT + 'return ' + returnValue + '\n';
            }
            const pureFunctionCode = `def ${funcNameForCode}(self, ${argsForDef.join(', ')}):\n${funcBody}`;

            // 2. Extract parameter metadata (name AND type) from the call block's connections.
            const parameters = argNames.map((argName, index) => {
                let inferredType = 'String'; // Default type
                const inputConnection = funcCallBlock.getInput('ARG' + index);
                if (inputConnection?.connection?.targetBlock()) {
                    const connectedBlock = inputConnection.connection.targetBlock();
                    const outputConnection = connectedBlock.outputConnection;
                    if (outputConnection?.getCheck()) {
                        const checks = outputConnection.getCheck();
                        if (checks?.length > 0) {
                            inferredType = checks[0];
                        }
                    }
                }
                return { name: argName, type: inferredType };
            });

            // 3. Generate the full script FOR EXECUTION. workspaceToCode will now work
            //    because our procedure call generator is fixed to use valueToCode.
            const fullScriptForExecution = pythonGenerator.workspaceToCode(workspace);

            return {
                code: fullScriptForExecution, // The full script to run now
                isFunctionalPower: true,
                // The metadata to be saved if the user clicks "Save" later
                metadata: {
                    function_name: functionName,
                    parameters: parameters,
                    python_code: pureFunctionCode // The pure function definition for the library
                }
            };

        } else {
            // --- Case 2: This is a "Script Power" (no function definition) ---
            console.log("Building debug payload for a simple script power.");

            const fullScriptForExecution = pythonGenerator.workspaceToCode(workspace);

            return {
                code: fullScriptForExecution,
                isFunctionalPower: false,
                metadata: { // No specific function metadata for scripts
                    function_name: null,
                    parameters: [],
                    python_code: fullScriptForExecution // For scripts, the whole thing is saved
                }
            };
        }
    }
    // --- Wire up the "Execute (Debug)" Button ---
    // In src/index.js, inside init()

    const executeButton = document.getElementById('executePowerButton');
    if (executeButton) {
        executeButton.addEventListener('click', async () => {
            console.log("Execute (Debug) button clicked.");

            // 1. Build the complete payload using our new helper function
            const payload = buildDebugPayload(workspace);

            // If payload is null, it means the workspace wasn't set up correctly for debugging.
            if (!payload) {
                return;
            }

            // For display, show the full script that will be executed
            const codeDisplay = document.getElementById('pythonCodeDisplay');
            if (codeDisplay) {
                codeDisplay.textContent = payload.code;
                if(window.Prism) Prism.highlightElement(codeDisplay);
            }

            // 2. Define the new magic command and prepare the arguments
            const command = '%mc_debug_and_define';

            // The argument is the full payload object, stringified as JSON
            const output = await executeIPythonCommand(command, JSON.stringify(payload));

            if (output) {
                alert("Debug Output:\n\n" + output);
            }
        });
    }


    document.body.addEventListener('loadPower', function(event) {
        if (!event.detail || !event.detail.powerData || !event.detail.powerData.blockly_json) {
            alert('Error: Could not load power. Data is missing.');
            return;
        }

        const powerData = event.detail.powerData;
        const mode = event.detail.mode;

        console.log(`Received power to load: '${powerData.name}' in '${mode}' mode.`);

        try {
            if (mode === 'replace') {
                if (workspace.getAllBlocks(false).length > 0) {
                    if (!confirm(`This will replace your current workspace with the power '${powerData.name}'. Are you sure?`)) {
                        return;
                    }
                }
                Blockly.serialization.workspaces.load(powerData.blockly_json, workspace);
                console.log("Workspace replaced successfully.");

            } else { // mode === 'add'

                console.log("Appending power to workspace...");
                const incomingJson = powerData.blockly_json;

                // --- THIS IS THE COMPLETE, CORRECT LOGIC ---

                // 1. Manually create/merge variables and create an ID remap dictionary.
                const variableMap = workspace.getVariableMap();
                const idRemap = {};
                if (incomingJson.variables) {
                    for (const newVar of incomingJson.variables) {
                        const existingVar = variableMap.getVariable(newVar.name);
                        if (existingVar && existingVar.getId() !== newVar.id) {
                            idRemap[newVar.id] = existingVar.getId();
                        } else if (!existingVar) {
                            workspace.createVariable(newVar.name, newVar.type, newVar.id);
                        }
                    }
                }

                // 2. If remappings are needed, stringify, replace all IDs, and parse back.
                let blocksToAppend = incomingJson.blocks;
                if (Object.keys(idRemap).length > 0 && blocksToAppend) {
                    let blockJsonString = JSON.stringify(blocksToAppend);
                    for (const oldId in idRemap) {
                        const newId = idRemap[oldId];
                        const searchRegExp = new RegExp(`"${escapeRegExp(oldId)}"`, 'g');
                        blockJsonString = blockJsonString.replace(searchRegExp, `"${newId}"`);
                    }
                    blocksToAppend = JSON.parse(blockJsonString);
                }

                // 3. Now, iterate through the top-level blocks and append them one by one.
                if (blocksToAppend && Array.isArray(blocksToAppend.blocks)) {
                    Blockly.Events.disable();
                    try {
                        const topBlocksJson = blocksToAppend.blocks;
                        for (const blockJson of topBlocksJson) {
                            // This is the key: calling .append for each individual block object.
                            Blockly.serialization.blocks.append(blockJson, workspace);
                        }
                        console.log(`Appended ${topBlocksJson.length} new block stack(s).`);
                    } finally {
                        Blockly.Events.enable();
                    }

                    // Clean up the layout to position the new blocks neatly.
                    if (workspace.getTopBlocks(false).length > 0) {
                         workspace.render();
                         workspace.cleanUp();
                    }
                }
            }

            autosaveWorkspace();

        } catch (e) {
            console.error("Error deserializing or loading workspace:", e);
            alert("Could not load the power. The file may be corrupted.");
        }
    });
    // document.body.addEventListener('loadPower', function(event) {
    //     if (!event.detail || !event.detail.powerData) {
    //         console.error("loadPower event triggered without powerData.", event.detail);
    //         return;
    //     }
    //
    //     const powerData = event.detail.powerData;
    //     const mode = event.detail.mode;
    //
    //     console.log(`Received power to load: '${powerData.name}' in '${mode}' mode.`);
    //
    //     if (!powerData.blockly_json || !powerData.blockly_json.blocks || !Array.isArray(powerData.blockly_json.blocks.blocks)) {
    //         alert(`Error: The power '${powerData.name}' has no saved block data.`);
    //         return;
    //     }
    //
    //     try {
    //         if (mode === 'replace') {
    //             if (workspace.getAllBlocks(false).length > 0) {
    //                 if (!confirm("This will replace your current workspace. Are you sure?")) {
    //                     return;
    //                 }
    //             }
    //             workspace.clear();
    //             Blockly.serialization.workspaces.load(powerData.blockly_json, workspace);
    //             console.log("Workspace replaced successfully.");
    //
    //         } else { // mode === 'add'
    //
    //             // --- CORRECTED APPEND AND POSITIONING LOGIC ---
    //             console.log("Appending blocks to workspace...");
    //
    //             // Get the array of top-level block definitions from the JSON.
    //             const topBlocksJson = powerData.blockly_json.blocks.blocks;
    //
    //             // 1. Get the metrics of the visible workspace area.
    //             const metrics = workspace.getMetrics();
    //
    //             // 2. Define a starting position for the new blocks, e.g., top-left of the view.
    //             //    Add a small offset to avoid placing blocks right at the edge.
    //             const PADDING = 20;
    //             let cursorX = metrics.viewLeft + PADDING;
    //             let cursorY = metrics.viewTop + PADDING;
    //
    //             // 3. Iterate through each top-level block definition in the array.
    //             for (const blockJson of topBlocksJson) {
    //                 // Set the position for the new block stack.
    //                 blockJson.x = cursorX;
    //                 blockJson.y = cursorY;
    //
    //                 // 4. Use blocks.append to add the block structure.
    //                 Blockly.serialization.blocks.append(blockJson, workspace);
    //
    //                 // 5. Update the cursor position for the next block stack to avoid overlap.
    //                 //    This creates a cascading effect.
    //                 cursorY += PADDING * 2;
    //             }
    //             console.log(`Appended ${topBlocksJson.length} new block stack(s) to the workspace.`);
    //             // --- END OF CORRECTED LOGIC ---
    //         }
    //
    //         // After loading, update the autosave with this new combined state
    //         autosaveWorkspace();
    //
    //     } catch (e) {
    //         console.error("Error deserializing or loading workspace:", e);
    //         alert("Could not load the power. The file may be corrupted.");
    //     }
    // });

    // --- Logic to handle resizing Blockly when panels collapse ---

    // Find the toggle buttons
    const libraryToggleBtn = document.querySelector('#power-library-panel .toggle-btn');
    const codeToggleBtn = document.querySelector('#editor-preview-pane .toggle-btn');

    // Create a debounced resize function
    const debouncedResize = debounce(() => {
        console.log("Resizing Blockly canvas...");
        // This is the official Blockly API to notify it of a resize.
        Blockly.svgResize(workspace);
    }, 100); // A short debounce is fine here

    // When either toggle button is clicked, call the resize function
    if (libraryToggleBtn) {
        libraryToggleBtn.addEventListener('click', debouncedResize);
    }
    if (codeToggleBtn) {
        codeToggleBtn.addEventListener('click', debouncedResize);
    }

    // Also resize when the window resizes
    window.addEventListener('resize', debouncedResize);

    // --- NEW: A dedicated function to trigger a Blockly resize ---
    const triggerBlocklyResize = debounce(() => {
        if (workspace) {
            console.log("Triggering Blockly resize...");
            // This is the official Blockly API to notify it of a container size change.
            Blockly.svgResize(workspace);
        }
    }, 100); // A 100ms debounce is plenty

    window.triggerBlocklyResize = triggerBlocklyResize;

    // --- Update the existing window resize listener to use the new helper ---
    window.addEventListener('resize', triggerBlocklyResize);
    
    // --- TEMPORARY DEBUGGING LISTENER ---
    // Add this anywhere inside the init() function.
    document.body.addEventListener('library-changed', (event) => {
        // If this message appears, the dispatch is working!
        console.log("Event 'library-changed' was successfully dispatched!");

        // This will show you the data that was sent with the event.
        // It should contain the powerId and powerName.
        console.log("Event Detail (data passed with dispatch):", event.detail);

        // You can use an alert for unmissable confirmation during testing.
        // alert(`Delete event dispatched for power name: ${event.detail.powerName}`);
    });
    // --- END OF DEBUGGING LISTENER ---
}

// --- Main Execution ---
// This listener waits for the entire HTML document to be parsed and ready.
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed.");

    // 1. NOW that the DOM is ready, start Alpine.
    //    It will scan the document and find all x-data attributes.
    Alpine.start();
    console.log("Alpine.js started.");

    // 2. Then, run our application's main initialization logic.
    init();
});