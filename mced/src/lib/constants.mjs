
export let MCED;

export function defineMineCraftConstants(Blockly) {


    MCED = {  // Export directly

        BlocklyNameTypes : {
            PROCEDURE: Blockly.Names.NameType.PROCEDURE,
            VARIABLE: Blockly.Names.NameType.VARIABLE
        },

        BlocklyUtils: {
            configureShadow: function (block, inputName) {
                let shadowValue = MCED.Defaults.values[block.type]?.[inputName]?.shadow;
                if (shadowValue) {
                    block.getInput(inputName).connection.setShadowDom(Blockly.utils.xml.textToDom(shadowValue));
                }
            },
            // get3dPickerShadow: () => '<shadow type="minecraft_vector_3d"><value name="X"><shadow type="math_number"><field name="NUM">0</field></shadow></value><value name="Y"><shadow type="math_number"><field name="NUM">0</field></shadow></value><value name="Z"><shadow type="math_number"><field name="NUM">0</field></shadow></value></shadow>',
            // getStepperShadow: (defaultValue) => `<shadow type="math_number"><field name="NUM">${defaultValue}</field></shadow>`,
        },

        Defaults: {values: {}},

        Colours:[
            { name: "White", hex: "#FFFFFF", id: "WHITE" },
            { name: "Orange", hex: "#D87F33", id: "ORANGE" },
            { name: "Magenta", hex: "#B24CD8", id: "MAGENTA" },
            { name: "Light Blue", hex: "#6699D8", id: "LIGHT_BLUE" },
            { name: "Yellow", hex: "#E5E533", id: "YELLOW" },
            { name: "Lime", hex: "#7FCC19", id: "LIME" },
            { name: "Pink", hex: "#F27FA5", id: "PINK" },
            { name: "Gray", hex: "#4C4C4C", id: "GRAY" },
            { name: "Light Gray", hex: "#999999", id: "LIGHT_GRAY" },
            { name: "Cyan", hex: "#4C7F99", id: "CYAN" }, // Existing Cyan
            { name: "Azure", hex: "#007FFF", id: "AZURE" }, // Added Azure - a bright, sky blue
            // Note: Minecraft's "Cyan" is often more teal/aqua. If the existing "Cyan"
            // is meant to be the Minecraft block, you might want a different hex for a true "Cyan" if needed,
            // or rename the existing one to "Aqua" or "Teal" if that's more accurate to the game.
            // For this example, I'm keeping the existing "Cyan" and adding a distinct "Azure".
            { name: "Purple", hex: "#7F3FB2", id: "PURPLE" },
            { name: "Blue", hex: "#334CB2", id: "BLUE" },
            { name: "Brown", hex: "#664C33", id: "BROWN" },
            { name: "Green", hex: "#667F33", id: "GREEN" },
            { name: "Red", hex: "#993333", id: "RED" },
            { name: "Black", hex: "#191919", id: "BLACK" },
            { name: "Tinted", hex: "#2A232B", id: "TINTED_GLASS_BLOCK" } // Added Tinted - dark, slightly purple-ish gray for tinted glass
                                                                    // The ID clearly indicates it might map to a specific block.
        ]
    };

    // --- A reusable, fully-resolved shadow block for a Vec3 ---
    const VECTOR_3D_SHADOW = `
        <shadow type="minecraft_vector_3d">
            <value name="X"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
            <value name="Y"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
            <value name="Z"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
        </shadow>`;

    const VECTOR_3D_SHADOW_Y_UP = `
        <shadow type="minecraft_vector_3d">
            <value name="X"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
            <value name="Y"><shadow type="math_number"><field name="NUM">1</field></shadow></value>
            <value name="Z"><shadow type="math_number"><field name="NUM">0</field></shadow></value>
        </shadow>`;

    // --- A reusable shadow for a standard Block Type input ---
    const BLOCK_TYPE_SHADOW = `
        <shadow type="minecraft_picker_world">
            <field name="MATERIAL_ID">STONE</field>
        </shadow>`;


    MCED.Defaults.values.minecraft_matrix_3d_euler = { // For shadow on other blocks
        YAW:   { shadow: '<shadow type="math_number"><field name="NUM">0</field></shadow>' },
        PITCH: { shadow: '<shadow type="math_number"><field name="NUM">0</field></shadow>' },
        ROLL:  { shadow: '<shadow type="math_number"><field name="NUM">0</field></shadow>' }
    };

    const matrix_elements = ["R00","R01","R02","R10","R11","R12","R20","R21","R22"];
    MCED.Defaults.values.minecraft_matrix_3d_elements = {};
    matrix_elements.forEach((el, index) => {
        let val = (index % 4 === 0) ? 1 : 0; // For identity matrix diagonal
        MCED.Defaults.values.minecraft_matrix_3d_elements[el] = {
            shadow: `<shadow type="math_number"><field name="NUM">${val}</field></shadow>`
        };
    });

    // MCED.Defaults.values['minecraft_vector_arithmetic'] = {
    //     A: { shadow: VECTOR_3D_SHADOW },
    //     B: { shadow: VECTOR_3D_SHADOW }
    // };
    
    MCED.Defaults.values['minecraft_vector_binary_op'] = {
        A: { shadow: VECTOR_3D_SHADOW },
        B: { shadow: VECTOR_3D_SHADOW }
    };

    MCED.Defaults.values['minecraft_vector_scalar_multiply'] = {
        A: { shadow: VECTOR_3D_SHADOW },
        B: { shadow: '<shadow type="math_number"><field name="NUM">1</field></shadow>' }
    };

    MCED.Defaults.values['minecraft_vector_dot_product'] = {
        A: { shadow: VECTOR_3D_SHADOW },
        B: { shadow: VECTOR_3D_SHADOW }
    };

    MCED.Defaults.values['minecraft_matrix_vector_multiply'] = {
        A: { shadow: '<shadow type="minecraft_matrix_3d_euler"></shadow>' },
        B: { shadow: VECTOR_3D_SHADOW }
    };
    // --- Digital Geometry Actions ---

    MCED.Defaults.values['minecraft_action_create_digital_line'] = {
        POINT1:     { shadow: VECTOR_3D_SHADOW },
        POINT2:     { shadow: VECTOR_3D_SHADOW },
        BLOCK_TYPE: { shadow: BLOCK_TYPE_SHADOW }
    };

    MCED.Defaults.values['minecraft_action_create_digital_plane'] = {
        NORMAL:          { shadow: VECTOR_3D_SHADOW_Y_UP },
        POINT_ON_PLANE:  { shadow: VECTOR_3D_SHADOW },
        BLOCK_TYPE:      { shadow: BLOCK_TYPE_SHADOW },
        OUTER_WIDTH:     { shadow: '<shadow type="math_number"><field name="NUM">10</field></shadow>' },
        OUTER_LENGTH:    { shadow: '<shadow type="math_number"><field name="NUM">10</field></shadow>' },
        PLANE_THICKNESS: { shadow: '<shadow type="math_number"><field name="NUM">1</field></shadow>' }
    };

    MCED.Defaults.values['minecraft_action_create_digital_ball'] = {
        CENTER:         { shadow: VECTOR_3D_SHADOW },
        RADIUS:         { shadow: '<shadow type="math_number"><field name="NUM">10</field></shadow>' },
        INNER_RADIUS:   { shadow: '<shadow type="math_number"><field name="NUM">0</field></shadow>' },
        BLOCK_TYPE:     { shadow: BLOCK_TYPE_SHADOW }
    };

    MCED.Defaults.values['minecraft_action_create_digital_tube'] = {
        POINT1:          { shadow: VECTOR_3D_SHADOW },
        POINT2:          { shadow: `<shadow type="minecraft_vector_3d"><value name="Y"><shadow type="math_number"><field name="NUM">10</field></shadow></value></shadow>` },
        OUTER_THICKNESS: { shadow: '<shadow type="math_number"><field name="NUM">3</field></shadow>' },
        INNER_THICKNESS: { shadow: '<shadow type="math_number"><field name="NUM">0</field></shadow>' },
        BLOCK_TYPE:      { shadow: BLOCK_TYPE_SHADOW }
    };

    MCED.Defaults.values['minecraft_action_create_digital_cube'] = {
        CENTER:              { shadow: VECTOR_3D_SHADOW },
        SIDE_LENGTH:         { shadow: '<shadow type="math_number"><field name="NUM">5</field></shadow>' },
        ROTATION_MATRIX:     { shadow: '<shadow type="minecraft_matrix_3d_euler"></shadow>' },
        BLOCK_TYPE:          { shadow: BLOCK_TYPE_SHADOW },
        INNER_OFFSET_FACTOR: { shadow: '<shadow type="math_number"><field name="NUM">0</field></shadow>' }
    };

    MCED.Defaults.values['minecraft_action_create_digital_disc'] = {
        NORMAL:         { shadow: VECTOR_3D_SHADOW_Y_UP },
        CENTER_POINT:   { shadow: VECTOR_3D_SHADOW },
        OUTER_RADIUS:   { shadow: '<shadow type="math_number"><field name="NUM">10</field></shadow>' },
        BLOCK_TYPE:     { shadow: BLOCK_TYPE_SHADOW },
        DISC_THICKNESS: { shadow: '<shadow type="math_number"><field name="NUM">1</field></shadow>' },
        INNER_RADIUS:   { shadow: '<shadow type="math_number"><field name="NUM">0</field></shadow>' }
    };


    MCED.Defaults.values['minecraft_action_set_block'] = {
        BLOCK_TYPE: { shadow: BLOCK_TYPE_SHADOW },
        POSITION:   { shadow: VECTOR_3D_SHADOW }
    };

    MCED.Defaults.values['minecraft_action_get_block'] = {
        POSITION:   { shadow: VECTOR_3D_SHADOW }
    };

    MCED.Defaults.values['minecraft_action_get_height'] = {
        POSITION:   { shadow: VECTOR_3D_SHADOW }
    };

    MCED.Defaults.values['minecraft_action_post_to_chat'] = {
        MESSAGE: { shadow: '<shadow type="text"><field name="TEXT">Hello, Minecraft!</field></shadow>' }
    };

    MCED.Defaults.values['minecraft_action_set_sign'] = {
        POSITION: { shadow: VECTOR_3D_SHADOW },
        LINE1:    { shadow: '<shadow type="text"><field name="TEXT"></field></shadow>' },
        LINE2:    { shadow: '<shadow type="text"><field name="TEXT">Hello!</field></shadow>' },
        LINE3:    { shadow: '<shadow type="text"><field name="TEXT"></field></shadow>' },
        LINE4:    { shadow: '<shadow type="text"><field name="TEXT"></field></shadow>' }
    };

    MCED.Defaults.values['minecraft_action_create_explosion'] = {
        POSITION: { shadow: VECTOR_3D_SHADOW },
        POWER:    { shadow: '<shadow type="math_number"><field name="NUM">4</field></shadow>' }
    };

    MCED.Defaults.values['minecraft_action_spawn_entity'] = {
        ENTITY_TYPE: {
            // Use one of your new entity pickers as the default shadow
            shadow: '<shadow type="minecraft_picker_entity_passive_mobs"><field name="ENTITY_ID">PIG</field></shadow>'
        },
        POSITION: {
            shadow: '<shadow type="minecraft_vector_3d"><value name="X"><shadow type="math_number"><field name="NUM">0</field></shadow></value><value name="Y"><shadow type="math_number"><field name="NUM">0</field></shadow></value><value name="Z"><shadow type="math_number"><field name="NUM">0</field></shadow></value></shadow>'
        }
    };

    // TODO do we even need this stuff??
    // Add Blockly.ALIGN_RIGHT
    Blockly.ALIGN_RIGHT = 'RIGHT'; //<-- Assign to Blockly.ALIGN_RIGHT

    // Add Blockly.Msg definitions
    Blockly.Msg = {  //<-- Assign to Blockly.Msg
        ...Blockly.Msg, // Important: Keep existing messages!
        MINECRAFT_COLUMN: "column",
        MINECRAFT_COLUMN_WIDTH: "width",
        MINECRAFT_COLUMN_HEIGHT: "height",
        MINECRAFT_COLUMN_TYPE: "type",
        MINECRAFT_COLUMN_FILLED: "filled",
        MINECRAFT_PLANE: "plane",
        CATEGORY_CRAFT: "Craft",
        CATEGORY_BLOCKS: "Blocks", //Added
        CATEGORY_POSITION: "Position", //Added
        MINECRAFT_SET_BLOCK: "set block",
        MINECRAFT_TYPE: "type",
        MINECRAFT_SET_BLOCKS: "set blocks",
        MINECRAFT_SIZE: "size",
        MINECRAFT_SET_FLOOR: "set floor",
        MINECRAFT_CREATE_DOOR: "create door",
        MINECRAFT_CREATE_DOOR_FACING: "facing",
        MINECRAFT_FACING_NORTH: "north",
        MINECRAFT_FACING_SOUTH: "south",
        MINECRAFT_FACING_EAST: "east",
        MINECRAFT_FACING_WEST: "west",
        MINECRAFT_CREATE_SHAPE: "create shape",
        MINECRAFT_SHAPE_CUBE: "cube",
        MINECRAFT_SHAPE_SPHERE: "sphere",
        MINECRAFT_SHAPE_PYRAMID: "pyramid",
        MINECRAFT_PRIMITIVE_TYPE: "type",
        MINECRAFT_CREATE_SHAPE_POSITION: "position",
        MINECRAFT_PRIMITIVE_SIZE: 'size',
        MINECRAFT_PRIMITIVE_RADIUS: 'radius',
        MINECRAFT_PRIMITIVE_BASE: 'base',
        MINECRAFT_VECTOR_DELTA: 'vector delta',
        MINECRAFT_VECTOR: 'vector',

        ADD_COMMENT: "Add Comment",
        CANNOT_DELETE_VARIABLE_PROCEDURE: "Can't delete the variable '%1' because it's part of the definition of the function '%2'",
        CHANGE_VALUE_TITLE: "Change value:",
        CLEAN_UP: "Clean up Blocks",
        COLLAPSE_ALL: "Collapse Blocks",
        COLLAPSE_BLOCK: "Collapse Block",
        COLOUR_BLEND_COLOUR1: "colour 1",
        COLOUR_BLEND_COLOUR2: "colour 2",
        COLOUR_BLEND_HELPURL: "http://meyerweb.com/eric/tools/color-blend/",
        COLOUR_BLEND_RATIO: "ratio",
        COLOUR_BLEND_TITLE: "blend",
        COLOUR_BLEND_TOOLTIP: "Blends two colours together with a given ratio (0.0 - 1.0).",
        COLOUR_PICKER_HELPURL: "https://en.wikipedia.org/wiki/Color",
        COLOUR_PICKER_TOOLTIP: "Choose a colour from the palette.",
        COLOUR_RANDOM_HELPURL: "http://randomcolour.com",
        COLOUR_RANDOM_TITLE: "random colour",
        COLOUR_RANDOM_TOOLTIP: "Choose a colour at random.",
        COLOUR_RGB_BLUE: "blue",
        COLOUR_RGB_GREEN: "green",
        COLOUR_RGB_HELPURL: "http://www.december.com/html/spec/colorper.html",
        COLOUR_RGB_RED: "red",
        COLOUR_RGB_TITLE: "colour with",
        COLOUR_RGB_TOOLTIP: "Create a colour with the specified amount of red, green, and blue. All values must be between 0 and 100.",
        CONTROLS_FLOW_STATEMENTS_HELPURL: "https://github.com/google/blockly/wiki/Loops#loop-termination-blocks",
        CONTROLS_FLOW_STATEMENTS_OPERATOR_BREAK: "break out of loop",
        CONTROLS_FLOW_STATEMENTS_OPERATOR_CONTINUE: "continue with next iteration of loop",
        CONTROLS_FLOW_STATEMENTS_TOOLTIP_BREAK: "Break out of the containing loop.",
        CONTROLS_FLOW_STATEMENTS_TOOLTIP_CONTINUE: "Skip the rest of this loop, and continue with the next iteration.",
        CONTROLS_FLOW_STATEMENTS_WARNING: "Warning: This block may only be used within a loop.",
        CONTROLS_FOREACH_HELPURL: "https://github.com/google/blockly/wiki/Loops#for-each",
        CONTROLS_FOREACH_TITLE: "for each item %1 in list %2",
        CONTROLS_FOREACH_TOOLTIP: "For each item in a list, set the variable '%1' to the item, and then do some statements.",
        CONTROLS_FOR_HELPURL: "https://github.com/google/blockly/wiki/Loops#count-with",
        CONTROLS_FOR_TITLE: "count with %1 from %2 to %3 by %4",
        CONTROLS_FOR_TOOLTIP: "Have the variable '%1' take on the values from the start number to the end number, counting by the specified interval, and do the specified blocks.",
        CONTROLS_IF_ELSEIF_TOOLTIP: "Add a condition to the if block.",
        CONTROLS_IF_ELSE_TOOLTIP: "Add a final, catch-all condition to the if block.",
        CONTROLS_IF_HELPURL: "https://github.com/google/blockly/wiki/IfElse",
        CONTROLS_IF_IF_TOOLTIP: "Add, remove, or reorder sections to reconfigure this if block.",
        CONTROLS_IF_MSG_ELSE: "else",
        CONTROLS_IF_MSG_ELSEIF: "else if",
        CONTROLS_IF_MSG_IF: "if",
        CONTROLS_IF_TOOLTIP_1: "If a value is true, then do some statements.",
        CONTROLS_IF_TOOLTIP_2: "If a value is true, then do the first block of statements. Otherwise, do the second block of statements.",
        CONTROLS_IF_TOOLTIP_3: "If the first value is true, then do the first block of statements. Otherwise, if the second value is true, do the second block of statements.",
        CONTROLS_IF_TOOLTIP_4: "If the first value is true, then do the first block of statements. Otherwise, if the second value is true, do the second block of statements. If none of the values are true, do the last block of statements.",
        CONTROLS_REPEAT_HELPURL: "https://en.wikipedia.org/wiki/For_loop",
        CONTROLS_REPEAT_INPUT_DO: "do",
        CONTROLS_REPEAT_TITLE: "repeat %1 times",
        CONTROLS_REPEAT_TOOLTIP: "Do some statements several times.",
        CONTROLS_WHILEUNTIL_HELPURL: "https://github.com/google/blockly/wiki/Loops#repeat",
        CONTROLS_WHILEUNTIL_OPERATOR_UNTIL: "repeat until",
        CONTROLS_WHILEUNTIL_OPERATOR_WHILE: "repeat while",
        CONTROLS_WHILEUNTIL_TOOLTIP_UNTIL: "While a value is false, then do some statements.",
        CONTROLS_WHILEUNTIL_TOOLTIP_WHILE: "While a value is true, then do some statements.",
        DELETE_ALL_BLOCKS: "Delete all %1 blocks?",
        DELETE_BLOCK: "Delete Block",
        DELETE_VARIABLE: "Delete the '%1' variable",
        DELETE_VARIABLE_CONFIRMATION: "Delete %1 uses of the '%2' variable?",
        DELETE_X_BLOCKS: "Delete %1 Blocks",
        DISABLE_BLOCK: "Disable Block",
        DUPLICATE_BLOCK: "Duplicate",
        ENABLE_BLOCK: "Enable Block",
        EXPAND_ALL: "Expand Blocks",
        EXPAND_BLOCK: "Expand Block",
        EXTERNAL_INPUTS: "External Inputs",
        HELP: "Help",
        INLINE_INPUTS: "Inline Inputs",
        IOS_CANCEL: "Cancel",
        IOS_ERROR: "Error",
        IOS_OK: "OK",
        IOS_PROCEDURES_ADD_INPUT: "+ Add Input",
        IOS_PROCEDURES_ALLOW_STATEMENTS: "Allow statements",
        IOS_PROCEDURES_DUPLICATE_INPUTS_ERROR: "This function has duplicate inputs.",
        IOS_PROCEDURES_INPUTS: "INPUTS",
        IOS_VARIABLES_ADD_BUTTON: "Add",
        IOS_VARIABLES_ADD_VARIABLE: "+ Add Variable",
        IOS_VARIABLES_DELETE_BUTTON: "Delete",
        IOS_VARIABLES_EMPTY_NAME_ERROR: "You can't use an empty variable name.",
        IOS_VARIABLES_RENAME_BUTTON: "Rename",
        IOS_VARIABLES_VARIABLE_NAME: "Variable name",
        LISTS_CREATE_EMPTY_HELPURL: "https://github.com/google/blockly/wiki/Lists#create-empty-list",
        LISTS_CREATE_EMPTY_TITLE: "create empty list",
        LISTS_CREATE_EMPTY_TOOLTIP: "Returns a list, of length 0, containing no data records",
        LISTS_CREATE_WITH_CONTAINER_TITLE_ADD: "list",
        LISTS_CREATE_WITH_CONTAINER_TOOLTIP: "Add, remove, or reorder sections to reconfigure this list block.",
        LISTS_CREATE_WITH_HELPURL: "https://github.com/google/blockly/wiki/Lists#create-list-with",
        LISTS_CREATE_WITH_INPUT_WITH: "create list with",
        LISTS_CREATE_WITH_ITEM_TOOLTIP: "Add an item to the list.",
        LISTS_CREATE_WITH_TOOLTIP: "Create a list with any number of items.",
        LISTS_GET_INDEX_FIRST: "first",
        LISTS_GET_INDEX_FROM_END: "# from end",
        LISTS_GET_INDEX_FROM_START: "#",
        LISTS_GET_INDEX_GET: "get",
        LISTS_GET_INDEX_GET_REMOVE: "get and remove",
        LISTS_GET_INDEX_LAST: "last",
        LISTS_GET_INDEX_RANDOM: "random",
        LISTS_GET_INDEX_REMOVE: "remove",
        LISTS_GET_INDEX_TAIL: "",
        LISTS_GET_INDEX_TOOLTIP_GET_FIRST: "Returns the first item in a list.",
        LISTS_GET_INDEX_TOOLTIP_GET_FROM: "Returns the item at the specified position in a list.",
        LISTS_GET_INDEX_TOOLTIP_GET_LAST: "Returns the last item in a list.",
        LISTS_GET_INDEX_TOOLTIP_GET_RANDOM: "Returns a random item in a list.",
        LISTS_GET_INDEX_TOOLTIP_GET_REMOVE_FIRST: "Removes and returns the first item in a list.",
        LISTS_GET_INDEX_TOOLTIP_GET_REMOVE_FROM: "Removes and returns the item at the specified position in a list.",
        LISTS_GET_INDEX_TOOLTIP_GET_REMOVE_LAST: "Removes and returns the last item in a list.",
        LISTS_GET_INDEX_TOOLTIP_GET_REMOVE_RANDOM: "Removes and returns a random item in a list.",
        LISTS_GET_INDEX_TOOLTIP_REMOVE_FIRST: "Removes the first item in a list.",
        LISTS_GET_INDEX_TOOLTIP_REMOVE_FROM: "Removes the item at the specified position in a list.",
        LISTS_GET_INDEX_TOOLTIP_REMOVE_LAST: "Removes the last item in a list.",
        LISTS_GET_INDEX_TOOLTIP_REMOVE_RANDOM: "Removes a random item in a list.",
        LISTS_GET_SUBLIST_END_FROM_END: "to # from end",
        LISTS_GET_SUBLIST_END_FROM_START: "to #",
        LISTS_GET_SUBLIST_END_LAST: "to last",
        LISTS_GET_SUBLIST_HELPURL: "https://github.com/google/blockly/wiki/Lists#getting-a-sublist",
        LISTS_GET_SUBLIST_START_FIRST: "get sub-list from first",
        LISTS_GET_SUBLIST_START_FROM_END: "get sub-list from # from end",
        LISTS_GET_SUBLIST_START_FROM_START: "get sub-list from #",
        LISTS_GET_SUBLIST_TAIL: "",
        LISTS_GET_SUBLIST_TOOLTIP: "Creates a copy of the specified portion of a list.",
        LISTS_INDEX_FROM_END_TOOLTIP: "%1 is the last item.",
        LISTS_INDEX_FROM_START_TOOLTIP: "%1 is the first item.",
        LISTS_INDEX_OF_FIRST: "find first occurrence of item",
        LISTS_INDEX_OF_HELPURL: "https://github.com/google/blockly/wiki/Lists#getting-items-from-a-list",
        LISTS_INDEX_OF_LAST: "find last occurrence of item",
        LISTS_INDEX_OF_TOOLTIP: "Returns the index of the first/last occurrence of the item in the list. Returns %1 if item is not found.",
        LISTS_INLIST: "in list",
        LISTS_ISEMPTY_HELPURL: "https://github.com/google/blockly/wiki/Lists#is-empty",
        LISTS_ISEMPTY_TITLE: "%1 is empty",
        LISTS_ISEMPTY_TOOLTIP: "Returns true if the list is empty.",
        LISTS_LENGTH_HELPURL: "https://github.com/google/blockly/wiki/Lists#length-of",
        LISTS_LENGTH_TITLE: "length of %1",
        LISTS_LENGTH_TOOLTIP: "Returns the length of a list.",
        LISTS_REPEAT_HELPURL: "https://github.com/google/blockly/wiki/Lists#create-list-with",
        LISTS_REPEAT_TITLE: "create list with item %1 repeated %2 times",
        LISTS_REPEAT_TOOLTIP: "Creates a list consisting of the given value repeated the specified number of times.",
        LISTS_REVERSE_HELPURL: "https://github.com/google/blockly/wiki/Lists#reversing-a-list",
        LISTS_REVERSE_MESSAGE0: "reverse %1",
        LISTS_REVERSE_TOOLTIP: "Reverse a copy of a list.",
        LISTS_SET_INDEX_HELPURL: "https://github.com/google/blockly/wiki/Lists#in-list--set",
        LISTS_SET_INDEX_INPUT_TO: "as",
        LISTS_SET_INDEX_INSERT: "insert at",
        LISTS_SET_INDEX_SET: "set",
        LISTS_SET_INDEX_TOOLTIP_INSERT_FIRST: "Inserts the item at the start of a list.",
        LISTS_SET_INDEX_TOOLTIP_INSERT_FROM: "Inserts the item at the specified position in a list.",
        LISTS_SET_INDEX_TOOLTIP_INSERT_LAST: "Append the item to the end of a list.",
        LISTS_SET_INDEX_TOOLTIP_INSERT_RANDOM: "Inserts the item randomly in a list.",
        LISTS_SET_INDEX_TOOLTIP_SET_FIRST: "Sets the first item in a list.",
        LISTS_SET_INDEX_TOOLTIP_SET_FROM: "Sets the item at the specified position in a list.",
        LISTS_SET_INDEX_TOOLTIP_SET_LAST: "Sets the last item in a list.",
        LISTS_SET_INDEX_TOOLTIP_SET_RANDOM: "Sets a random item in a list.",
        LISTS_SORT_HELPURL: "https://github.com/google/blockly/wiki/Lists#sorting-a-list",
        LISTS_SORT_ORDER_ASCENDING: "ascending",
        LISTS_SORT_ORDER_DESCENDING: "descending",
        LISTS_SORT_TITLE: "sort %1 %2 %3",
        LISTS_SORT_TOOLTIP: "Sort a copy of a list.",
        LISTS_SORT_TYPE_IGNORECASE: "alphabetic, ignore case",
        LISTS_SORT_TYPE_NUMERIC: "numeric",
        LISTS_SORT_TYPE_TEXT: "alphabetic",
        LISTS_SPLIT_HELPURL: "https://github.com/google/blockly/wiki/Lists#splitting-strings-and-joining-lists",
        LISTS_SPLIT_LIST_FROM_TEXT: "make list from text",
        LISTS_SPLIT_TEXT_FROM_LIST: "make text from list",
        LISTS_SPLIT_TOOLTIP_JOIN: "Join a list of texts into one text, separated by a delimiter.",
        LISTS_SPLIT_TOOLTIP_SPLIT: "Split text into a list of texts, breaking at each delimiter.",
        LISTS_SPLIT_WITH_DELIMITER: "with delimiter",
        LOGIC_BOOLEAN_FALSE: "false",
        LOGIC_BOOLEAN_HELPURL: "https://github.com/google/blockly/wiki/Logic#values",
        LOGIC_BOOLEAN_TOOLTIP: "Returns either true or false.",
        LOGIC_BOOLEAN_TRUE: "true",
        LOGIC_COMPARE_HELPURL: "https://en.wikipedia.org/wiki/Inequality_(mathematics)",
        LOGIC_COMPARE_TOOLTIP_EQ: "Return true if both inputs equal each other.",
        LOGIC_COMPARE_TOOLTIP_GT: "Return true if the first input is greater than the second input.",
        LOGIC_COMPARE_TOOLTIP_GTE: "Return true if the first input is greater than or equal to the second input.",
        LOGIC_COMPARE_TOOLTIP_LT: "Return true if the first input is smaller than the second input.",
        LOGIC_COMPARE_TOOLTIP_LTE: "Return true if the first input is smaller than or equal to the second input.",
        LOGIC_COMPARE_TOOLTIP_NEQ: "Return true if both inputs are not equal to each other.",
        LOGIC_NEGATE_HELPURL: "https://github.com/google/blockly/wiki/Logic#not",
        LOGIC_NEGATE_TITLE: "not %1",
        LOGIC_NEGATE_TOOLTIP: "Returns true if the input is false. Returns false if the input is true.",
        LOGIC_NULL: "null",
        LOGIC_NULL_HELPURL: "https://en.wikipedia.org/wiki/Nullable_type",
        LOGIC_NULL_TOOLTIP: "Returns null.",
        LOGIC_OPERATION_AND: "and",
        LOGIC_OPERATION_HELPURL: "https://github.com/google/blockly/wiki/Logic#logical-operations",
        LOGIC_OPERATION_OR: "or",
        LOGIC_OPERATION_TOOLTIP_AND: "Return true if both inputs are true.",
        LOGIC_OPERATION_TOOLTIP_OR: "Return true if at least one of the inputs is true.",
        LOGIC_TERNARY_CONDITION: "test",
        LOGIC_TERNARY_HELPURL: "https://en.wikipedia.org/wiki/%3F:",
        LOGIC_TERNARY_IF_FALSE: "if false",
        LOGIC_TERNARY_IF_TRUE: "if true",
        LOGIC_TERNARY_TOOLTIP: "Check the condition in 'test'. If the condition is true, returns the 'if true' value, otherwise returns the 'if false' value.",
        MATH_ADDITION_SYMBOL: "+",
        MATH_ARITHMETIC_HELPURL: "https://en.wikipedia.org/wiki/Arithmetic",
        MATH_ARITHMETIC_TOOLTIP_ADD: "Return the sum of the two numbers.",
        MATH_ARITHMETIC_TOOLTIP_DIVIDE: "Return the quotient of the two numbers.",
        MATH_ARITHMETIC_TOOLTIP_MINUS: "Return the difference of the two numbers.",
        MATH_ARITHMETIC_TOOLTIP_MULTIPLY: "Return the product of the two numbers.",
        MATH_ARITHMETIC_TOOLTIP_POWER: "Return the first number raised to the power of the second number.",
        MATH_CHANGE_HELPURL: "https://en.wikipedia.org/wiki/Programming_idiom#Incrementing_a_counter",
        MATH_CHANGE_TITLE: "change %1 by %2",
        MATH_CHANGE_TOOLTIP: "Add a number to variable '%1'.",
        MATH_CONSTANT_HELPURL: "https://en.wikipedia.org/wiki/Mathematical_constant",
        MATH_CONSTANT_TOOLTIP: "Return one of the common constants: π (3.141…), e (2.718…), φ (1.618…), sqrt(2) (1.414…), sqrt(½) (0.707…), or ∞ (infinity).",
        MATH_CONSTRAIN_HELPURL: "https://en.wikipedia.org/wiki/Clamping_(graphics)",
        MATH_CONSTRAIN_TITLE: "constrain %1 low %2 high %3",
        MATH_CONSTRAIN_TOOLTIP: "Constrain a number to be between the specified limits (inclusive).",
        MATH_DIVISION_SYMBOL: "÷",
        MATH_IS_DIVISIBLE_BY: "is divisible by",
        MATH_IS_EVEN: "is even",
        MATH_IS_NEGATIVE: "is negative",
        MATH_IS_ODD: "is odd",
        MATH_IS_POSITIVE: "is positive",
        MATH_IS_PRIME: "is prime",
        MATH_IS_TOOLTIP: "Check if a number is an even, odd, prime, whole, positive, negative, or if it is divisible by certain number. Returns true or false.",
        MATH_IS_WHOLE: "is whole",
        MATH_MODULO_HELPURL: "https://en.wikipedia.org/wiki/Modulo_operation",
        MATH_MODULO_TITLE: "remainder of %1 ÷ %2",
        MATH_MODULO_TOOLTIP: "Return the remainder from dividing the two numbers.",
        MATH_MULTIPLICATION_SYMBOL: "×",
        MATH_NUMBER_HELPURL: "https://en.wikipedia.org/wiki/Number",
        MATH_NUMBER_TOOLTIP: "A number.",
        MATH_ONLIST_HELPURL: "",
        MATH_ONLIST_OPERATOR_AVERAGE: "average of list",
        MATH_ONLIST_OPERATOR_MAX: "max of list",
        MATH_ONLIST_OPERATOR_MEDIAN: "median of list",
        MATH_ONLIST_OPERATOR_MIN: "min of list",
        MATH_ONLIST_OPERATOR_MODE: "modes of list",
        MATH_ONLIST_OPERATOR_RANDOM: "random item of list",
        MATH_ONLIST_OPERATOR_STD_DEV: "standard deviation of list",
        MATH_ONLIST_OPERATOR_SUM: "sum of list",
        MATH_ONLIST_TOOLTIP_AVERAGE: "Return the average (arithmetic mean) of the numeric values in the list.",
        MATH_ONLIST_TOOLTIP_MAX: "Return the largest number in the list.",
        MATH_ONLIST_TOOLTIP_MEDIAN: "Return the median number in the list.",
        MATH_ONLIST_TOOLTIP_MIN: "Return the smallest number in the list.",
        MATH_ONLIST_TOOLTIP_MODE: "Return a list of the most common item(s) in the list.",
        MATH_ONLIST_TOOLTIP_RANDOM: "Return a random element from the list.",
        MATH_ONLIST_TOOLTIP_STD_DEV: "Return the standard deviation of the list.",
        MATH_ONLIST_TOOLTIP_SUM: "Return the sum of all the numbers in the list.",
        MATH_POWER_SYMBOL: "^",
        MATH_RANDOM_FLOAT_HELPURL: "https://en.wikipedia.org/wiki/Random_number_generation",
        MATH_RANDOM_FLOAT_TITLE_RANDOM: "random fraction",
        MATH_RANDOM_FLOAT_TOOLTIP: "Return a random fraction between 0.0 (inclusive) and 1.0 (exclusive).",
        MATH_RANDOM_INT_HELPURL: "https://en.wikipedia.org/wiki/Random_number_generation",
        MATH_RANDOM_INT_TITLE: "random integer from %1 to %2",
        MATH_RANDOM_INT_TOOLTIP: "Return a random integer between the two specified limits, inclusive.",
        MATH_ROUND_HELPURL: "https://en.wikipedia.org/wiki/Rounding",
        MATH_ROUND_OPERATOR_ROUND: "round",
        MATH_ROUND_OPERATOR_ROUNDDOWN: "round down",
        MATH_ROUND_OPERATOR_ROUNDUP: "round up",
        MATH_ROUND_TOOLTIP: "Round a number up or down.",
        MATH_SINGLE_HELPURL: "https://en.wikipedia.org/wiki/Square_root",
        MATH_SINGLE_OP_ABSOLUTE: "absolute",
        MATH_SINGLE_OP_ROOT: "square root",
        MATH_SINGLE_TOOLTIP_ABS: "Return the absolute value of a number.",
        MATH_SINGLE_TOOLTIP_EXP: "Return e to the power of a number.",
        MATH_SINGLE_TOOLTIP_LN: "Return the natural logarithm of a number.",
        MATH_SINGLE_TOOLTIP_LOG10: "Return the base 10 logarithm of a number.",
        MATH_SINGLE_TOOLTIP_NEG: "Return the negation of a number.",
        MATH_SINGLE_TOOLTIP_POW10: "Return 10 to the power of a number.",
        MATH_SINGLE_TOOLTIP_ROOT: "Return the square root of a number.",
        MATH_SUBTRACTION_SYMBOL: "-",
        MATH_TRIG_ACOS: "acos",
        MATH_TRIG_ASIN: "asin",
        MATH_TRIG_ATAN: "atan",
        MATH_TRIG_COS: "cos",
        MATH_TRIG_HELPURL: "https://en.wikipedia.org/wiki/Trigonometric_functions",
        MATH_TRIG_SIN: "sin",
        MATH_TRIG_TAN: "tan",
        MATH_TRIG_TOOLTIP_ACOS: "Return the arccosine of a number.",
        MATH_TRIG_TOOLTIP_ASIN: "Return the arcsine of a number.",
        MATH_TRIG_TOOLTIP_ATAN: "Return the arctangent of a number.",
        MATH_TRIG_TOOLTIP_COS: "Return the cosine of a degree (not radian).",
        MATH_TRIG_TOOLTIP_SIN: "Return the sine of a degree (not radian).",
        MATH_TRIG_TOOLTIP_TAN: "Return the tangent of a degree (not radian).",
        NEW_VARIABLE: "Create variable...",
        NEW_VARIABLE_TITLE: "New variable name:",
        ORDINAL_NUMBER_SUFFIX: "",
        PROCEDURES_ALLOW_STATEMENTS: "allow statements",
        PROCEDURES_BEFORE_PARAMS: "with:",
        PROCEDURES_CALLNORETURN_HELPURL: "https://en.wikipedia.org/wiki/Subroutine",
        PROCEDURES_CALLNORETURN_TOOLTIP: "Run the user-defined function '%1'.",
        PROCEDURES_CALLRETURN_HELPURL: "https://en.wikipedia.org/wiki/Subroutine",
        PROCEDURES_CALLRETURN_TOOLTIP: "Run the user-defined function '%1' and use its output.",
        PROCEDURES_CALL_BEFORE_PARAMS: "with:",
        PROCEDURES_CREATE_DO: "Create '%1'",
        PROCEDURES_DEFNORETURN_COMMENT: "Describe this function...",
        PROCEDURES_DEFNORETURN_DO: "",
        PROCEDURES_DEFNORETURN_HELPURL: "https://en.wikipedia.org/wiki/Subroutine",
        PROCEDURES_DEFNORETURN_PROCEDURE: "do something",
        PROCEDURES_DEFNORETURN_TITLE: "to",
        PROCEDURES_DEFNORETURN_TOOLTIP: "Creates a function with no output.",
        PROCEDURES_DEFRETURN_HELPURL: "https://en.wikipedia.org/wiki/Subroutine",
        PROCEDURES_DEFRETURN_RETURN: "return",
        PROCEDURES_DEFRETURN_TOOLTIP: "Creates a function with an output.",
        PROCEDURES_DEF_DUPLICATE_WARNING: "Warning: This function has duplicate parameters.",
        PROCEDURES_HIGHLIGHT_DEF: "Highlight function definition",
        PROCEDURES_IFRETURN_HELPURL: "http://c2.com/cgi/wiki?GuardClause",
        PROCEDURES_IFRETURN_TOOLTIP: "If a value is true, then return a second value.",
        PROCEDURES_IFRETURN_WARNING: "Warning: This block may be used only within a function definition.",
        PROCEDURES_MUTATORARG_TITLE: "input name:",
        PROCEDURES_MUTATORARG_TOOLTIP: "Add an input to the function.",
        PROCEDURES_MUTATORCONTAINER_TITLE: "inputs",
        PROCEDURES_MUTATORCONTAINER_TOOLTIP: "Add, remove, or reorder inputs to this function.",
        PROCEDURE_ALREADY_EXISTS: "A procedure named '%1' already exists.",
        REDO: "Redo",
        REMOVE_COMMENT: "Remove Comment",
        RENAME_VARIABLE: "Rename variable...",
        RENAME_VARIABLE_TITLE: "Rename all '%1' variables to:",
        TEXT_APPEND_HELPURL: "https://github.com/google/blockly/wiki/Text#text-modification",
        TEXT_APPEND_TITLE: "to %1 append text %2",
        TEXT_APPEND_TOOLTIP: "Append some text to variable '%1'.",
        TEXT_CHANGECASE_HELPURL: "https://github.com/google/blockly/wiki/Text#adjusting-text-case",
        TEXT_CHANGECASE_OPERATOR_LOWERCASE: "to lower case",
        TEXT_CHANGECASE_OPERATOR_TITLECASE: "to Title Case",
        TEXT_CHANGECASE_OPERATOR_UPPERCASE: "to UPPER CASE",
        TEXT_CHANGECASE_TOOLTIP: "Return a copy of the text in a different case.",
        TEXT_CHARAT_FIRST: "get first letter",
        TEXT_CHARAT_FROM_END: "get letter # from end",
        TEXT_CHARAT_FROM_START: "get letter #",
        TEXT_CHARAT_HELPURL: "https://github.com/google/blockly/wiki/Text#extracting-text",
        TEXT_CHARAT_LAST: "get last letter",
        TEXT_CHARAT_RANDOM: "get random letter",
        TEXT_CHARAT_TAIL: "",
        TEXT_CHARAT_TITLE: "in text %1 %2",
        TEXT_CHARAT_TOOLTIP: "Returns the letter at the specified position.",
        TEXT_COUNT_HELPURL: "https://github.com/google/blockly/wiki/Text#counting-substrings",
        TEXT_COUNT_MESSAGE0: "count %1 in %2",
        TEXT_COUNT_TOOLTIP: "Count how many times some text occurs within some other text.",
        TEXT_CREATE_JOIN_ITEM_TOOLTIP: "Add an item to the text.",
        TEXT_CREATE_JOIN_TITLE_JOIN: "join",
        TEXT_CREATE_JOIN_TOOLTIP: "Add, remove, or reorder sections to reconfigure this text block.",
        TEXT_GET_SUBSTRING_END_FROM_END: "to letter # from end",
        TEXT_GET_SUBSTRING_END_FROM_START: "to letter #",
        TEXT_GET_SUBSTRING_END_LAST: "to last letter",
        TEXT_GET_SUBSTRING_HELPURL: "https://github.com/google/blockly/wiki/Text#extracting-a-region-of-text",
        TEXT_GET_SUBSTRING_INPUT_IN_TEXT: "in text",
        TEXT_GET_SUBSTRING_START_FIRST: "get substring from first letter",
        TEXT_GET_SUBSTRING_START_FROM_END: "get substring from letter # from end",
        TEXT_GET_SUBSTRING_START_FROM_START: "get substring from letter #",
        TEXT_GET_SUBSTRING_TAIL: "",
        TEXT_GET_SUBSTRING_TOOLTIP: "Returns a specified portion of the text.",
        TEXT_INDEXOF_HELPURL: "https://github.com/google/blockly/wiki/Text#finding-text",
        TEXT_INDEXOF_OPERATOR_FIRST: "find first occurrence of text",
        TEXT_INDEXOF_OPERATOR_LAST: "find last occurrence of text",
        TEXT_INDEXOF_TITLE: "in text %1 %2 %3",
        TEXT_INDEXOF_TOOLTIP: "Returns the index of the first/last occurrence of the first text in the second text. Returns %1 if text is not found.",
        TEXT_ISEMPTY_HELPURL: "https://github.com/google/blockly/wiki/Text#checking-for-empty-text",
        TEXT_ISEMPTY_TITLE: "%1 is empty",
        TEXT_ISEMPTY_TOOLTIP: "Returns true if the provided text is empty.",
        TEXT_JOIN_HELPURL: "https://github.com/google/blockly/wiki/Text#text-creation",
        TEXT_JOIN_TITLE_CREATEWITH: "create text with",
        TEXT_JOIN_TOOLTIP: "Create a piece of text by joining together any number of items.",
        TEXT_LENGTH_HELPURL: "https://github.com/google/blockly/wiki/Text#text-modification",
        TEXT_LENGTH_TITLE: "length of %1",
        TEXT_LENGTH_TOOLTIP: "Returns the number of letters (including spaces) in the provided text.",
        TEXT_PRINT_HELPURL: "https://github.com/google/blockly/wiki/Text#printing-text",
        TEXT_PRINT_TITLE: "print %1",
        TEXT_PRINT_TOOLTIP: "Print the specified text, number or other value.",
        TEXT_PROMPT_HELPURL: "https://github.com/google/blockly/wiki/Text#getting-input-from-the-user",
        TEXT_PROMPT_TOOLTIP_NUMBER: "Prompt for user for a number.",
        TEXT_PROMPT_TOOLTIP_TEXT: "Prompt for user for some text.",
        TEXT_PROMPT_TYPE_NUMBER: "prompt for number with message",
        TEXT_PROMPT_TYPE_TEXT: "prompt for text with message",
        TEXT_REPLACE_HELPURL: "https://github.com/google/blockly/wiki/Text#replacing-substrings",
        TEXT_REPLACE_MESSAGE0: "replace %1 with %2 in %3",
        TEXT_REPLACE_TOOLTIP: "Replace all occurances of some text within some other text.",
        TEXT_REVERSE_HELPURL: "https://github.com/google/blockly/wiki/Text#reversing-text",
        TEXT_REVERSE_MESSAGE0: "reverse %1",
        TEXT_REVERSE_TOOLTIP: "Reverses the order of the characters in the text.",
        TEXT_TEXT_HELPURL: "https://en.wikipedia.org/wiki/String_(computer_science)",
        TEXT_TEXT_TOOLTIP: "A letter, word, or line of text.",
        TEXT_TRIM_HELPURL: "https://github.com/google/blockly/wiki/Text#trimming-removing-spaces",
        TEXT_TRIM_OPERATOR_BOTH: "trim spaces from both sides of",
        TEXT_TRIM_OPERATOR_LEFT: "trim spaces from left side of",
        TEXT_TRIM_OPERATOR_RIGHT: "trim spaces from right side of",
        TEXT_TRIM_TOOLTIP: "Return a copy of the text with spaces removed from one or both ends.",
        TODAY: "Today",
        UNDO: "Undo",
        VARIABLES_DEFAULT_NAME: "item",
        VARIABLES_GET_CREATE_SET: "Create 'set %1'",
        VARIABLES_GET_HELPURL: "https://github.com/google/blockly/wiki/Variables#get",
        VARIABLES_GET_TOOLTIP: "Returns the value of this variable.",
        VARIABLES_SET: "set %1 to %2",
        VARIABLES_SET_CREATE_GET: "Create 'get %1'",
        VARIABLES_SET_HELPURL: "https://github.com/google/blockly/wiki/Variables#set",
        VARIABLES_SET_TOOLTIP: "Sets this variable to be equal to the input.",
        VARIABLE_ALREADY_EXISTS: "A variable named '%1' already exists.",
        VARIABLE_ALREADY_EXISTS_FOR_ANOTHER_TYPE: "A variable named '%1' already exists for another variable of type '%2'.",
        MATH_HUE: "230",
        LOOPS_HUE: "120",
        LISTS_HUE: "260",
        LOGIC_HUE: "210",
        VARIABLES_HUE: "330",
        TEXTS_HUE: "160",
        PROCEDURES_HUE: "290",
        COLOUR_HUE: "20",

        LOOP: "loop"

    };

}