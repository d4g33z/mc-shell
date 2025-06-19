import Alpine from 'alpinejs';
import 'htmx.org'; // Imports for its side-effect of initializing on the window
import 'htmx-ext-json-enc'; // Imports the extension
import Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/themes/prism-okaidia.css';

import * as Blockly from 'blockly';
import { pythonGenerator } from 'blockly/python';
import { defineMineCraftBlocks } from "./blocks/mc.mjs";
import { defineMineCraftMaterialBlocks } from "./blocks/materials.mjs";
import { defineMinecraftEntityBlocks } from "./blocks/entities.mjs";
import { defineMineCraftConstants } from "./lib/constants.mjs";
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
     */
    async function handleSavePower() {
        console.log("Handling save power...");

        // 1. Get the form element itself
        const formElement = document.getElementById('savePowerForm');
        if (!formElement) {
            console.error("Save Power form not found!");
            return;
        }

        // 2. Use the FormData API to easily get all form values into an object
        const formData = new FormData(formElement);
        const formDataObject = Object.fromEntries(formData.entries());

        if (!formDataObject.name) {
            alert("Please enter a name for your power.");
            return;
        }

        // 3. Get the current state of the Blockly workspace
        const blocklyJson = Blockly.serialization.workspaces.save(workspace);
        const pythonCode = pythonGenerator.workspaceToCode(workspace);

        // 4. Assemble the complete "Power Object" by merging the form data and workspace data
        const powerDataObject = {
            name: formDataObject.name,
            description: formDataObject.description,
            category: formDataObject.category || "General",
            blockly_json: blocklyJson,
            python_code: pythonCode,
            parameters: [] // Placeholder for now
        };

        console.log("Sending power data to server:", powerDataObject);

        // 5. POST the complete object to the new Flask endpoint
        try {
            const response = await fetch('/api/powers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(powerDataObject),
            });

            if (response.ok) {
                const result = await response.json();
                console.log("Power saved successfully!", result);
                alert(`Power "${formDataObject.name}" saved successfully!`);

                // --- FIX: Dispatch events instead of manipulating state ---
                // Announce that the modal should close
                window.dispatchEvent(new CustomEvent('power-saved-successfully'));
                // Announce that the library list should refresh
                // window.htmlx.trigger(document.getElementById('power-list'), 'load');

                // // Dispatch the custom event to close the modal
                // window.dispatchEvent(new CustomEvent('close-save-modal'));
                //
                // // Trigger a refresh of the power list using htmx
                // const powerListElement = document.getElementById('power-list');
                // // --- THE FIX ---
                // // Announce that a power was saved by dispatching a custom event on the body.
                // console.log("Save successful. Dispatching 'powerSaved' event.");
                // document.body.dispatchEvent(new CustomEvent('powerSaved', { bubbles: true }));
                // --- END OF FIX ---

        //         if (powerListElement) {
        //             htmx.trigger(powerListElement, 'load');
        //         }

            } else {
                console.error('Error saving power:', response.status, await response.text());
                alert('Failed to save power. See console for details.');
            }
        } catch (error) {
            console.error('Network error while saving power:', error);
            alert('Network error. Could not save power.');
        }
    }

    // Ensure the event listener for the save button is active in your init() function
    // This code should already be in your init() function
    // const confirmSaveButton = document.getElementById('confirmSaveButton');
    // if (confirmSaveButton) {
    //     confirmSaveButton.addEventListener('click', handleSavePower);
    // }


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
    const toolboxXml = `
    <xml xmlns="https://developers.google.com/blockly/xml" id="toolbox" style="display: none">
    <category name="Logic" colour="%{BKY_LOGIC_HUE}">
        <block type="logic_boolean">
            <field name="BOOL">TRUE</field>
        </block>
        <block type="controls_if"></block>
        <block type="controls_if">
            <mutation else="1"></mutation>
        </block>
        <block type="controls_if">
            <mutation elseif="1" else="1"></mutation>
        </block>
        <block type="logic_compare">
            <field name="OP">EQ</field>
        </block>
        <block type="logic_operation">
            <field name="OP">AND</field>
        </block>
        <block type="logic_negate"></block>
        <block type="logic_null"></block>
        <block type="logic_ternary"></block>
    </category>
    <category name="Loops" colour="%{BKY_LOOPS_HUE}">
        <block type="controls_repeat_ext">
            <value name="TIMES">
                <shadow type="math_number">
                    <field name="NUM">10</field>
                </shadow>
            </value>
        </block>
        <block type="controls_whileUntil">
            <field name="MODE">WHILE</field>
        </block>
        <block type="controls_for">
            <field name="VAR" id="!gX(y%~iMy{cR:F;7#m)">i</field>
            <value name="FROM">
                <shadow type="math_number">
                    <field name="NUM">1</field>
                </shadow>
            </value>
            <value name="TO">
                <shadow type="math_number">
                    <field name="NUM">10</field>
                </shadow>
            </value>
            <value name="BY">
                <shadow type="math_number">
                    <field name="NUM">1</field>
                </shadow>
            </value>
        </block>
        <block type="controls_forEach">
            <field name="VAR" id="O=g^GX@oH{1m$R@nN{8}">j</field>
        </block>
        <block type="controls_flow_statements">
            <field name="FLOW">BREAK</field>
        </block>
    </category>
    <category name="Math" colour="%{BKY_MATH_HUE}">
        <block type="math_number">
            <field name="NUM">0</field>
        </block>
        <block type="math_arithmetic">
            <field name="OP">ADD</field>
            <value name="A">
                <shadow type="math_number">
                    <field name="NUM">1</field>
                </shadow>
            </value>
            <value name="B">
                <shadow type="math_number">
                    <field name="NUM">1</field>
                </shadow>
            </value>
        </block>
        <block type="math_single">
            <field name="OP">ROOT</field>
            <value name="NUM">
                <shadow type="math_number">
                    <field name="NUM">9</field>
                </shadow>
            </value>
        </block>
        <block type="math_trig">
            <field name="OP">SIN</field>
            <value name="NUM">
                <shadow type="math_number">
                    <field name="NUM">45</field>
                </shadow>
            </value>
        </block>
        <block type="math_constant">
            <field name="CONSTANT">PI</field>
        </block>
        <block type="math_number_property">
            <mutation divisor_input="false"></mutation>
            <field name="PROPERTY">EVEN</field>
            <value name="NUMBER_TO_CHECK">
                <shadow type="math_number">
                    <field name="NUM">0</field>
                </shadow>
            </value>
        </block>
        <block type="math_round">
            <field name="OP">ROUND</field>
            <value name="NUM">
                <shadow type="math_number">
                    <field name="NUM">3.1</field>
                </shadow>
            </value>
        </block>
        <block type="math_on_list">
            <mutation op="SUM"></mutation>
            <field name="OP">SUM</field>
        </block>
        <block type="math_modulo">
            <value name="DIVIDEND">
                <shadow type="math_number">
                    <field name="NUM">64</field>
                </shadow>
            </value>
            <value name="DIVISOR">
                <shadow type="math_number">
                    <field name="NUM">10</field>
                </shadow>
            </value>
        </block>
        <block type="math_constrain">
            <value name="VALUE">
                <shadow type="math_number">
                    <field name="NUM">50</field>
                </shadow>
            </value>
            <value name="LOW">
                <shadow type="math_number">
                    <field name="NUM">1</field>
                </shadow>
            </value>
            <value name="HIGH">
                <shadow type="math_number">
                    <field name="NUM">100</field>
                </shadow>
            </value>
        </block>
        <block type="math_random_int">
            <value name="FROM">
                <shadow type="math_number">
                    <field name="NUM">1</field>
                </shadow>
            </value>
            <value name="TO">
                <shadow type="math_number">
                    <field name="NUM">100</field>
                </shadow>
            </value>
        </block>
        <block type="math_random_float"></block>
        <block type="math_atan2">
            <value name="X">
                <shadow type="math_number">
                    <field name="NUM">1</field>
                </shadow>
            </value>
            <value name="Y">
                <shadow type="math_number">
                    <field name="NUM">1</field>
                </shadow>
            </value>
        </block>
    </category>
    <category name="Text" colour="%{BKY_TEXTS_HUE}">
        <block type="text">
            <field name="TEXT"></field>
        </block>
        <block type="text_join">
            <mutation items="2"></mutation>
        </block>
        <block type="text_append">
            <field name="VAR" id="r#_uLPNR*v4Fk950:Xl$">item</field>
            <value name="TEXT">
                <shadow type="text">
                    <field name="TEXT"></field>
                </shadow>
            </value>
        </block>
        <block type="text_length">
            <value name="VALUE">
                <shadow type="text">
                    <field name="TEXT">abc</field>
                </shadow>
            </value>
        </block>
        <block type="text_isEmpty">
            <value name="VALUE">
                <shadow type="text">
                    <field name="TEXT"></field>
                </shadow>
            </value>
        </block>
        <block type="text_indexOf">
            <field name="END">FIRST</field>
            <value name="VALUE">
                <block type="variables_get">
                    <field name="VAR" id="aH[(Lg?9x}hJ@5c6)pT}">text</field>
                </block>
            </value>
            <value name="FIND">
                <shadow type="text">
                    <field name="TEXT">abc</field>
                </shadow>
            </value>
        </block>
        <block type="text_charAt">
            <mutation at="true"></mutation>
            <field name="WHERE">FROM_START</field>
            <value name="VALUE">
                <block type="variables_get">
                    <field name="VAR" id="aH[(Lg?9x}hJ@5c6)pT}">text</field>
                </block>
            </value>
        </block>
        <block type="text_getSubstring">
            <mutation at1="true" at2="true"></mutation>
            <field name="WHERE1">FROM_START</field>
            <field name="WHERE2">FROM_START</field>
            <value name="STRING">
                <block type="variables_get">
                    <field name="VAR" id="aH[(Lg?9x}hJ@5c6)pT}">text</field>
                </block>
            </value>
        </block>
        <block type="text_changeCase">
            <field name="CASE">UPPERCASE</field>
            <value name="TEXT">
                <shadow type="text">
                    <field name="TEXT">abc</field>
                </shadow>
            </value>
        </block>
        <block type="text_trim">
            <field name="MODE">BOTH</field>
            <value name="TEXT">
                <shadow type="text">
                    <field name="TEXT">abc</field>
                </shadow>
            </value>
        </block>
        <block type="text_print">
            <value name="TEXT">
                <shadow type="text">
                    <field name="TEXT">abc</field>
                </shadow>
            </value>
        </block>
        <block type="text_prompt_ext">
            <mutation type="TEXT"></mutation>
            <field name="TYPE">TEXT</field>
            <value name="TEXT">
                <shadow type="text">
                    <field name="TEXT">abc</field>
                </shadow>
            </value>
        </block>
    </category>
    <category name="Lists" colour="%{BKY_LISTS_HUE}">
        <block type="lists_create_with">
            <mutation items="0"></mutation>
        </block>
        <block type="lists_create_with">
            <mutation items="3"></mutation>
        </block>
        <block type="lists_repeat">
            <value name="NUM">
                <shadow type="math_number">
                    <field name="NUM">5</field>
                </shadow>
            </value>
        </block>
        <block type="lists_length"></block>
        <block type="lists_isEmpty"></block>
        <block type="lists_indexOf">
            <field name="END">FIRST</field>
            <value name="VALUE">
                <block type="variables_get">
                    <field name="VAR" id="!g9E0785E:sOYJAbCH{^">list</field>
                </block>
            </value>
        </block>
        <block type="lists_getIndex">
            <mutation statement="false" at="true"></mutation>
            <field name="MODE">GET</field>
            <field name="WHERE">FROM_START</field>
            <value name="VALUE">
                <block type="variables_get">
                    <field name="VAR" id="!g9E0785E:sOYJAbCH{^">list</field>
                </block>
            </value>
        </block>
        <block type="lists_setIndex">
            <mutation at="true"></mutation>
            <field name="MODE">SET</field>
            <field name="WHERE">FROM_START</field>
            <value name="LIST">
                <block type="variables_get">
                    <field name="VAR" id="!g9E0785E:sOYJAbCH{^">list</field>
                </block>
            </value>
        </block>
        <block type="lists_getSublist">
            <mutation at1="true" at2="true"></mutation>
            <field name="WHERE1">FROM_START</field>
            <field name="WHERE2">FROM_START</field>
            <value name="LIST">
                <block type="variables_get">
                    <field name="VAR" id="!g9E0785E:sOYJAbCH{^">list</field>
                </block>
            </value>
        </block>
        <block type="lists_split">
            <mutation mode="SPLIT"></mutation>
            <field name="MODE">SPLIT</field>
            <value name="DELIM">
                <shadow type="text">
                    <field name="TEXT">,</field>
                </shadow>
            </value>
        </block>
        <block type="lists_sort">
            <field name="TYPE">NUMERIC</field>
            <field name="DIRECTION">1</field>
        </block>
        <block type="lists_reverse"></block>
    </category>
    <category name="Variables" colour="%{BKY_VARIABLES_HUE}" custom="VARIABLE"></category>
    <category name="Functions" colour="%{BKY_PROCEDURES_HUE}" custom="PROCEDURE"></category>
    <category name="Colour" colour="%{BKY_COLOUR_HUE}">
        <block type="minecraft_coloured_block_picker"></block>
        <!--        <block type="colour_picker"></block>-->
        <!--        <block type="colour_random"></block>-->
        <!--        <block type="colour_rgb"></block>-->
        <!--        <block type="colour_blend"></block>-->
    </category>
    <sep></sep>
    <category name="Vector Math" colour="#5b80a5">

        <block type="minecraft_matrix_3d_euler">
            <value name="YAW"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
            <value name="PITCH"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
            <value name="ROLL"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
        </block>
        <block type="minecraft_vector_arithmetic">
            <field name="OP">ADD</field> <value name="A">
            <shadow type="minecraft_vector_3d">
            </shadow>
        </value>
            <value name="B">
                <shadow type="minecraft_vector_3d">
                </shadow>
            </value>
        </block>

        <block type="minecraft_vector_arithmetic">
            <field name="OP">MATRIX_MULTIPLY</field> <value name="A">
            <shadow type="minecraft_matrix_3d_euler"> <value name="YAW"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                <value name="PITCH"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                <value name="ROLL"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
            </shadow>
        </value>
            <value name="B">
                <shadow type="minecraft_vector_3d"> <value name="X"><shadow type="math_number"><field name="NUM">1</field></shadow></value>
                    <value name="Y"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                    <value name="Z"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                </shadow>
            </value>
        </block>

    </category>
    <category name="Position" colour="#0099CC">

        <block type="minecraft_vector_3d">
            <value name="X">
                <shadow type="math_number">
                    <field name="NUM">0</field>
                </shadow>
            </value>
            <value name="Y">
                <shadow type="math_number">
                    <field name="NUM">0</field>
                </shadow>
            </value>
            <value name="Z">
                <shadow type="math_number">
                    <field name="NUM">0</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_vector_2d"></block>
        <block type="minecraft_vector_delta">
            <value name="X">
                <shadow type="math_number">
                    <field name="NUM">1</field>
                </shadow>
            </value>
            <value name="Y">
                <shadow type="math_number">
                    <field name="NUM">0</field>
                </shadow>
            </value>
            <value name="Z">
                <shadow type="math_number">
                    <field name="NUM">0</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_position_player"></block>
        <!--          <block type="minecraft_position_entity">-->
        <!--               <value name="ENTITY">-->
        <!--                   <shadow type="minecraft_entity_entity"></shadow> </value>-->
        <!--          </block>-->
        <block type="minecraft_position_get_direction"></block>
        <!--          <block type="minecraft_position_look_at">-->
        <!--               <value name="TARGET">-->
        <!--                   <shadow type="minecraft_vector_3d">-->
        <!--                         <value name="X">-->
        <!--                           <shadow type="math_number">-->
        <!--                             <field name="NUM">0</field>-->
        <!--                           </shadow>-->
        <!--                         </value>-->
        <!--                         <value name="Y">-->
        <!--                           <shadow type="math_number">-->
        <!--                             <field name="NUM">0</field>-->
        <!--                           </shadow>-->
        <!--                         </value>-->
        <!--                         <value name="Z">-->
        <!--                           <shadow type="math_number">-->
        <!--                             <field name="NUM">0</field>-->
        <!--                           </shadow>-->
        <!--                         </value>-->
        <!--                   </shadow>-->
        <!--               </value>-->
        <!--          </block>-->
        <block type="minecraft_position_here"></block>
    </category>
    <category name="Digital Geometry" colour="#4a90e2">
        <block type="minecraft_action_create_digital_line">
            <value name="POINT1">
                <shadow type="minecraft_vector_3d">
                    <value name="X"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                    <value name="Y"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                    <value name="Z"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                </shadow>
            </value>
            <value name="POINT2">
                <shadow type="minecraft_vector_3d">
                    <value name="X"><shadow type="math_number"><field name="NUM">10</field></shadow></value>
                    <value name="Y"><shadow type="math_number"><field name="NUM">10</field></shadow></value>
                    <value name="Z"><shadow type="math_number"><field name="NUM">10</field></shadow></value>
                </shadow>
            </value>
            <value name="BLOCK_TYPE">
                <shadow type="minecraft_picker_miscellaneous">
                    <field name="MATERIAL_ID">STONE</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_action_create_digital_tube">
            <value name="POINT1">
                <shadow type="minecraft_vector_3d">
                    <value name="X"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                    <value name="Y"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                    <value name="Z"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                </shadow>
            </value>
            <value name="POINT2">
                <shadow type="minecraft_vector_3d">
                    <value name="X"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                    <value name="Y"><shadow type="math_number"><field name="NUM">10</field></shadow></value>
                    <value name="Z"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                </shadow>
            </value>
            <value name="OUTER_THICKNESS">
                <shadow type="math_number"><field name="NUM">3</field></shadow>
            </value>
            <value name="BLOCK_TYPE">
                <shadow type="minecraft_picker_miscellaneous"><field name="TYPE">STONE</field></shadow>
            </value>
            <value name="INNER_THICKNESS">
                <shadow type="math_number"><field name="NUM">0</field></shadow>
            </value>
        </block>
        <block type="minecraft_action_create_digital_ball">
            <value name="CENTER">
                <shadow type="minecraft_vector_3d">
                    <field name="X">0</field><field name="Y">0</field><field name="Z">0</field>
                </shadow>
            </value>
            <value name="RADIUS">
                <shadow type="math_number"><field name="NUM">5</field></shadow>
            </value>
            <value name="BLOCK_TYPE">
                <!--              <shadow type="minecraft_block_world"><field name="TYPE">STONE</field></shadow>-->
                <shadow type="minecraft_picker_miscellaneous"><field name="TYPE">STONE</field></shadow>
            </value>
            <value name="INNER_RADIUS">
                <shadow type="math_number"><field name="NUM">0</field></shadow>
            </value>
        </block>
        <block type="minecraft_action_create_digital_cube">
            <value name="CENTER">
                <shadow type="minecraft_vector_3d">
                    <field name="X">0</field><field name="Y">0</field><field name="Z">0</field>
                </shadow>
            </value>
            <value name="SIDE_LENGTH">
                <shadow type="math_number"><field name="NUM">5</field></shadow>
            </value>
            <value name="ROTATION_MATRIX">
                <shadow type="minecraft_matrix_3d_euler"> <value name="YAW"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                    <value name="PITCH"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                    <value name="ROLL"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                </shadow>
            </value>
            <value name="BLOCK_TYPE">
                <!--              <shadow type="minecraft_block_world"><field name="TYPE">STONE</field></shadow>-->
                <shadow type="minecraft_picker_miscellaneous"><field name="TYPE">STONE</field></shadow>
            </value>
            <value name="INNER_OFFSET_FACTOR">
                <shadow type="math_number"><field name="NUM">0</field></shadow>
            </value>
        </block>
        <block type="minecraft_action_create_digital_plane">
            <value name="NORMAL">
                <shadow type="minecraft_vector_3d">
                    <value name="X"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                    <value name="Y"><shadow type="math_number"><field name="NUM">1</field></shadow></value>
                    <value name="Z"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                </shadow>
            </value>
            <value name="POINT_ON_PLANE">
                <shadow type="minecraft_vector_3d">
                    <field name="X">0</field><field name="Y">0</field><field name="Z">0</field>
                </shadow>
            </value>
            <value name="BLOCK_TYPE">
                <!--                <shadow type="minecraft_block_world"><field name="TYPE">STONE</field></shadow>-->
                <shadow type="minecraft_picker_miscellaneous"><field name="TYPE">STONE</field></shadow>
            </value>
            <value name="OUTER_RECT_DIMS"> <shadow type="minecraft_vector_2d">
                <field name="W">10</field>
                <field name="H">10</field>
            </shadow>
            </value>
            <value name="PLANE_THICKNESS">
                <shadow type="math_number"><field name="NUM">1</field></shadow>
            </value>
            <value name="INNER_RECT_DIMS">
                <shadow type="minecraft_vector_2d">
                    <field name="W">0</field><field name="H">0</field>
                </shadow>
            </value>
            <value name="RECT_CENTER_OFFSET">
                <shadow type="minecraft_vector_3d">
                    <field name="X">0</field><field name="Y">0</field><field name="Z">0</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_action_create_digital_disc">
            <value name="NORMAL">
                <shadow type="minecraft_vector_3d">
                    <value name="X"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                    <value name="Y"><shadow type="math_number"><field name="NUM">1</field></shadow></value>
                    <value name="Z"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                </shadow>
            </value>
            <value name="CENTER_POINT">
                <shadow type="minecraft_vector_3d">
                    <field name="X">0</field><field name="Y">0</field><field name="Z">0</field>
                </shadow>
            </value>
            <value name="OUTER_RADIUS">
                <shadow type="math_number"><field name="NUM">10</field></shadow>
            </value>
            <value name="BLOCK_TYPE">
                <!--                <shadow type="minecraft_block_world"><field name="TYPE">STONE</field></shadow>-->
                <shadow type="minecraft_picker_miscellaneous"><field name="TYPE">STONE</field></shadow>
            </value>
            <value name="DISC_THICKNESS">
                <shadow type="math_number"><field name="NUM">1</field></shadow>
            </value>
            <value name="INNER_RADIUS">
                <shadow type="math_number"><field name="NUM">0</field></shadow>
            </value>
        </block>
    </category>
    <sep></sep>
    <category name="Materials" colour="#777777">
        <block type="minecraft_material_wool">
            <value name="COLOUR">
                <shadow type="minecraft_coloured_block_picker">
                    <field name="MINECRAFT_COLOUR_ID">WHITE</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_material_terracotta">
            <value name="COLOUR">
                <shadow type="minecraft_coloured_block_picker">
                    <field name="MINECRAFT_COLOUR_ID">WHITE</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_material_stained_glass">
            <value name="COLOUR">
                <shadow type="minecraft_coloured_block_picker">
                    <field name="MINECRAFT_COLOUR_ID">WHITE</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_material_stained_glass_pane">
            <value name="COLOUR">
                <shadow type="minecraft_coloured_block_picker">
                    <field name="MINECRAFT_COLOUR_ID">WHITE</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_material_concrete">
            <value name="COLOUR">
                <shadow type="minecraft_coloured_block_picker">
                    <field name="MINECRAFT_COLOUR_ID">WHITE</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_material_concrete_powder">
            <value name="COLOUR">
                <shadow type="minecraft_coloured_block_picker">
                    <field name="MINECRAFT_COLOUR_ID">WHITE</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_material_candle">
            <value name="COLOUR">
                <shadow type="minecraft_coloured_block_picker">
                    <field name="MINECRAFT_COLOUR_ID">WHITE</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_material_bed">
            <value name="COLOUR">
                <shadow type="minecraft_coloured_block_picker">
                    <field name="MINECRAFT_COLOUR_ID">WHITE</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_material_banner">
            <value name="COLOUR">
                <shadow type="minecraft_coloured_block_picker">
                    <field name="MINECRAFT_COLOUR_ID">WHITE</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_material_shulker_box">
            <value name="COLOUR">
                <shadow type="minecraft_coloured_block_picker">
                    <field name="MINECRAFT_COLOUR_ID">WHITE</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_material_carpet">
            <value name="COLOUR">
                <shadow type="minecraft_coloured_block_picker">
                    <field name="MINECRAFT_COLOUR_ID">WHITE</field>
                </shadow>
            </value>
        </block>
        <block type="minecraft_material_glazed_terracotta">
            <value name="COLOUR">
                <shadow type="minecraft_coloured_block_picker">
                    <field name="MINECRAFT_COLOUR_ID">WHITE</field>
                </shadow>
            </value>
        </block>
        <sep></sep>
        <block type="minecraft_picker_world"></block>
        <block type="minecraft_picker_ores"></block>
        <block type="minecraft_picker_wood_planks"></block>
        <block type="minecraft_picker_wood_logs"></block>
        <block type="minecraft_picker_wood_full"></block>
        <block type="minecraft_picker_stone_bricks"></block>
        <block type="minecraft_picker_glass"></block>
        <block type="minecraft_picker_redstone_components"></block>
        <block type="minecraft_picker_stairs"></block>
        <block type="minecraft_picker_slabs"></block>
        <block type="minecraft_picker_fences"></block>
        <block type="minecraft_picker_gates"></block>
        <block type="minecraft_picker_doors"></block>
        <sep></sep>
        <block type="minecraft_picker_miscellaneous"></block>
    </category>
    <category name="Entities" colour="#5b5ba5">
        <block type="minecraft_picker_entity_hostile_mobs"></block>
        <block type="minecraft_picker_entity_minecarts"></block>
        <block type="minecraft_picker_entity_miscellaneous_entities"></block>
        <block type="minecraft_picker_entity_passive_mobs"></block>
        <block type="minecraft_picker_entity_projectiles"></block>
        <block type="minecraft_picker_entity_utility_and_special"></block>
    </category>
    <category name="World Actions" colour="#4C97FF">
        <block type="minecraft_action_spawn_entity">
            <value name="ENTITY_TYPE">
                <shadow type="minecraft_picker_entity_passive_mobs">
                    <field name="ENTITY_ID">SHEEP</field>
                </shadow>
            </value>
            <value name="POSITION">
                <shadow type="minecraft_vector_3d">
                    <value name="X"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                    <value name="Y"><shadow type="math_number"><field name="NUM">5</field></shadow></value>
                    <value name="Z"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
                </shadow>
            </value>
        </block>
      </category>
</xml>    
`;

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

    // --- Wire up the "Execute (Debug)" Button ---
    const executeButton = document.getElementById('executePowerButton');
    if (executeButton) {
        executeButton.addEventListener('click', async () => {
            console.log("Execute (Debug) button clicked.");

            // 1. Get the current Python code from the display
            const codeToExecute = pythonGenerator.workspaceToCode(workspace);
            if (!codeToExecute) {
                alert("Workspace is empty. Nothing to execute.");
                return;
            }

            // For debugging, let's update the display immediately
            const codeDisplay = document.getElementById('pythonCodeDisplay');
            if (codeDisplay) {
                codeDisplay.textContent = codeToExecute;
                if(window.Prism) Prism.highlightElement(codeDisplay);
            }

            // 2. Define the magic command and pass the generated code as its arguments
            const command = '%mc_create_script';
            const output = await executeIPythonCommand(command, codeToExecute);

            if (output) {
                // Optionally, display the output from the shell
                alert("Execution Output:\n\n" + output);
            }
        });
    }

    // --- Add the event listener for loading powers ---
    document.body.addEventListener('loadPower', function(event) {
        if (!event.detail || !event.detail.powerData) {
            console.error("loadPower event triggered without powerData.", event.detail);
            return;
        }

        const powerData = event.detail.powerData;
        const mode = event.detail.mode; // 'replace' or 'add'

        console.log(`Received power to load: '${powerData.name}' in '${mode}' mode.`);

        // Check if there is actual block data to load
        if (!powerData.blockly_json) {
            alert(`Error: The power '${powerData.name}' has no saved block data.`);
            return;
        }

        try {
            if (mode === 'replace') {
                // Confirm with the user before overwriting their work
                if (workspace.getAllBlocks(false).length > 0) {
                    if (!confirm("This will replace your current workspace. Are you sure?")) {
                        return; // User clicked cancel
                    }
                }
                workspace.clear();
            }

            // Load the new blocks from the 'blockly_json' field of the power data
            Blockly.serialization.workspaces.load(powerData.blockly_json, workspace);

            // After loading, update the autosave with this new state
            autosaveWorkspace();

        } catch (e) {
            console.error("Error deserializing or loading workspace:", e);
            alert("Could not load the power. The file may be corrupted.");
        }
    });


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