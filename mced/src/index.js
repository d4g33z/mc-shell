// --- Initialize Alpine.js for the Editor UI (e.g., the Save Modal) ---
import Alpine from 'alpinejs';

// Make Alpine available globally on the window object for x-data attributes.
window.Alpine = Alpine;


import 'htmx.org';

import * as Blockly from 'blockly';
import * as Prism from 'prismjs';

import 'prismjs/components/prism-python';
import 'prismjs/themes/prism-okaidia.css';

import { pythonGenerator } from 'blockly/python';

// --- NEW: Import the htmx listener initializer ---
import { initializeHtmxListeners } from './lib/htmx_listeners.mjs';

import { installMCGenerator} from "./generators/python/mc.mjs";
import { installMCMaterialsGenerator} from "./generators/python/materials.mjs";
import { installMCEntityGenerator } from "./generators/python/entities.mjs";

import {defineMineCraftBlocklyUtils} from "./lib/utils.mjs";
import {defineMineCraftConstants} from "./lib/constants.mjs";
import {defineMineCraftBlocks} from "./blocks/mc.mjs";
import {defineMineCraftMaterialBlocks} from "./blocks/materials.mjs";
import {defineMinecraftEntityBlocks} from "./blocks/entities.mjs";

// Define the structure for a completely empty workspace
const BLANK_WORKSPACE_JSON = {
    "blocks": { "languageVersion": 0, "blocks": [] },
    "variables": []
};

// A module-scoped variable to hold the main workspace instance
let workspace;


async function init() {
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
     * Gathers data from the editor and modal, then posts it to the server.
     */
    async function handleSavePower() {
        console.log("Handling save power...");

        // 1. Get metadata from the modal form
        const powerName = document.getElementById('powerName').value;
        const powerDescription = document.getElementById('powerDescription').value;
        const powerCategory = document.getElementById('powerCategory').value;

        if (!powerName) {
            alert("Please enter a name for your power.");
            return;
        }

        // 2. Get the current state of the Blockly workspace
        const blocklyJson = Blockly.serialization.workspaces.save(workspace);
        const pythonCode = pythonGenerator.workspaceToCode(workspace);

        // 3. Assemble the complete "Power Object"
        const powerDataObject = {
            name: powerName,
            description: powerDescription,
            category: powerCategory || "General", // Default category
            blockly_json: blocklyJson,
            python_code: pythonCode,
            parameters: [] // Placeholder for now. We will implement parameter extraction later.
        };

        console.log("Sending power data to server:", powerDataObject);

        // 4. POST the data to the new Flask endpoint
        try {
            const response = await fetch('/api/powers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(powerDataObject),
            });

            if (response.ok) {
                const result = await response.json();
                console.log("Power saved successfully!", result);
                alert(`Power "${powerName}" saved successfully!`);
                // Close the modal after saving
                document.querySelector('.modal-root').__x.data.isModalOpen = false;

                // TODO: Refresh the power library list using htmx
                // htmx.trigger('#power-library-panel', 'load');
            } else {
                console.error('Error saving power:', response.status, await response.text());
                alert('Failed to save power. See console for details.');
            }
        } catch (error) {
            console.error('Network error while saving power:', error);
            alert('Network error. Could not save power.');
        }
    }

    initializeHtmxListeners();

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
        json: BLANK_WORKSPACE_JSON
    });

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

    // --- Wire up UI Buttons ---
    const clearButton = document.getElementById('clearWorkspaceButton');
    if (clearButton) {
        clearButton.addEventListener('click', () => {
            workspace.clear();
            console.log("Workspace cleared.");
        });
    }

    // Add other button listeners for Save, Load, Execute here later.
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