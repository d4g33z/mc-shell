console.log("mc.mjs: Start of file execution");

import {MCED} from "../lib/constants.mjs"; //Importing here!


export function defineMineCraftBlocks(Blockly) {

    Blockly.Blocks['dummy_block'] = {
        init: function () {
            console.log("mc.mjs: Inside init() function of ...");
        }

    };

    // -- Colours Category ---:/

    Blockly.Blocks['minecraft_coloured_block_picker'] = {
      init: function() {
        this.appendDummyInput()
            .appendField(new Blockly.FieldMinecraftColour(MCED.Colours[0].id), "MINECRAFT_COLOUR_ID");
            // The second argument to FieldMinecraftColour (opt_validator) is optional.
            // MINECRAFT_COLOURS[0].id sets 'WHITE' as the default.
        this.setOutput(true, "MinecraftColour"); // This block outputs our custom colour type
        this.setColour("%{BKY_COLOUR_HUE}"); // Use Blockly's standard colour hue
        this.setTooltip("Select a Minecraft block colour.");
      }
    };

    // --- Position Category ---:/

    Blockly.Blocks['minecraft_matrix_3d_elements'] = {
        init: function () {
            this.appendDummyInput().appendField("Rotation Matrix (Elements)");
            this.appendValueInput("R00").setCheck("Number").setAlign(Blockly.ALIGN_RIGHT).appendField("r00");
            this.appendValueInput("R01").setCheck("Number").setAlign(Blockly.ALIGN_RIGHT).appendField("r01");
            this.appendValueInput("R02").setCheck("Number").setAlign(Blockly.ALIGN_RIGHT).appendField("r02");
            this.appendValueInput("R10").setCheck("Number").setAlign(Blockly.ALIGN_RIGHT).appendField("r10");
            this.appendValueInput("R11").setCheck("Number").setAlign(Blockly.ALIGN_RIGHT).appendField("r11");
            this.appendValueInput("R12").setCheck("Number").setAlign(Blockly.ALIGN_RIGHT).appendField("r12");
            this.appendValueInput("R20").setCheck("Number").setAlign(Blockly.ALIGN_RIGHT).appendField("r20");
            this.appendValueInput("R21").setCheck("Number").setAlign(Blockly.ALIGN_RIGHT).appendField("r21");
            this.appendValueInput("R22").setCheck("Number").setAlign(Blockly.ALIGN_RIGHT).appendField("r22");
            this.setOutput(true, "3DMatrix");
            this.setColour(210); // A different color for matrices
            this.setTooltip("Define a 3x3 rotation matrix by its elements.");
            this.setInputsInline(false); // Easier to read for 9 inputs
        }
    };

    Blockly.Blocks['minecraft_matrix_3d_euler'] = {
        init: function () {
            this.appendDummyInput().appendField("Rotation Matrix (Euler Angles)");
            this.appendValueInput("YAW")
                .setCheck("Number")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Yaw (Z, degrees)");
            this.appendValueInput("PITCH")
                .setCheck("Number")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Pitch (Y, degrees)");
            this.appendValueInput("ROLL")
                .setCheck("Number")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Roll (X, degrees)");
            this.setOutput(true, "3DMatrix");
            this.setColour(210);
            this.setTooltip("Define a 3x3 rotation matrix from Euler angles (yaw, pitch, roll).");
            this.setInputsInline(false);
        }
    };

    Blockly.Blocks['minecraft_vector_2d'] = {
      init: function() {
        this.appendDummyInput()
            .appendField("w:") // Or "dim1:", "u:"
            .appendField(new Blockly.FieldNumber(0), "W") // Using FieldNumber for direct number input
            .appendField(" h:") // Or "dim2:", "v:"
            .appendField(new Blockly.FieldNumber(0), "H");
        this.setOutput(true, "2DVector"); // Output type
        this.setColour(180); // A distinct color for 2D vectors
        this.setTooltip("A 2D vector or dimension (width, height/length).");
        this.setInputsInline(true); // Keep it compact
      }
    };

    Blockly.Blocks['minecraft_vector_3d'] = {
        init: function () {
            if (this.isInFlyout) {
                this.appendDummyInput()
                    .appendField(Blockly.Msg.MINECRAFT_VECTOR);
                this.setOutput(true, "3DVector");
                this.setColour(160);
            } else {
                this.appendDummyInput()
                    .appendField("x:")
                    .appendField(new Blockly.FieldTextInput("0"), "X")
                    .appendField("y:")
                    .appendField(new Blockly.FieldTextInput("0"), "Y")
                    .appendField("z:")
                    .appendField(new Blockly.FieldTextInput("0"), "Z");
                this.setOutput(true, "3DVector");
                this.setColour(160);
            }
        }
    };

    Blockly.Blocks['minecraft_vector_delta'] = {
        init: function () {
            if (this.isInFlyout) {
                this.appendDummyInput()
                    .appendField(Blockly.Msg.MINECRAFT_VECTOR_DELTA);
                this.setOutput(true, "3DVector");
                this.setColour(160);
            } else {
                this.appendDummyInput()
                    .appendField("x:")
                    .appendField(new Blockly.FieldNumber(1), "X") // Use FieldNumber
                    .appendField("y:")
                    .appendField(new Blockly.FieldNumber(0), "Y")
                    .appendField("z:")
                    .appendField(new Blockly.FieldNumber(0), "Z");
                this.setOutput(true, "3DVector");
                this.setColour(160);
            }
        }
    };

    Blockly.Blocks['minecraft_position_player'] = {
        init: function () {
            this.appendDummyInput()
                .appendField("player position");
            this.setOutput(true, "3DVector");
            this.setColour(160);
        }
    };

    Blockly.Blocks['minecraft_position_here'] = {
        init: function () {
            this.appendDummyInput()
                .appendField("here");
            this.setOutput(true, '3DVector');
            this.setColour(160);
        }
    };

    Blockly.Blocks['minecraft_position_get_direction'] = {
        init: function () {
            this.appendDummyInput()
                .appendField("player direction");
            this.setOutput(true, "3DUnitVector");
            this.setColour(160);
        }
    };


    // --- Vector Math Category ---:/

    Blockly.Blocks['minecraft_vector_arithmetic'] = {
        init: function() {
            this.appendValueInput("A")
                .setCheck(["3DVector", "3DMatrix"]); // Input A can be a Vector or Matrix now
            this.appendDummyInput()
                .appendField(new Blockly.FieldDropdown([
                    ["+", "ADD"],
                    ["-", "SUBTRACT"],
                    ["× (scalar)", "MULTIPLY"],
                    ["• (dot product)", "DOT"],
                    ["× (cross product)", "CROSS"],
                    ["Rotated by Matrix", "MATRIX_MULTIPLY"] // <-- NEW OPERATION ADDED
                ]), "OP");
            this.appendValueInput("B")
                .setCheck(["3DVector", "Number"]);
            this.setInputsInline(true);
            this.setOutput(true, ["3DVector", "Number"]);
            this.setColour(180);
            this.setTooltip(() => { // Dynamic tooltip
                const op = this.getFieldValue('OP');
                const tooltips = {
                    'ADD': 'Returns the sum of two vectors.',
                    'SUBTRACT': 'Returns the difference of two vectors.',
                    'MULTIPLY': 'Returns the vector multiplied by a scalar.',
                    'DOT': 'Returns the dot product of two vectors (a number).',
                    'CROSS': 'Returns the cross product of two vectors (a new vector perpendicular to both).',
                    'MATRIX_MULTIPLY': 'Returns a new vector by transforming a vector with a rotation matrix.'
                };
                return tooltips[op] || 'Performs vector arithmetic.';
            });
            this.setHelpUrl("");
        },

        onchange: function(event) {
            // Only run on user-made changes to the operator field
            if (event.type !== Blockly.Events.BLOCK_CHANGE || event.element !== 'field' || event.name !== 'OP') {
                return;
            }

            const op = this.getFieldValue('OP');
            const inputA = this.getInput('A');
            const inputB = this.getInput('B');

            if (op === 'MATRIX_MULTIPLY') {
                // A is Matrix, B is Vector -> outputs Vector
                inputA.setCheck('3DMatrix');
                inputB.setCheck('3DVector');
                this.setOutput(true, '3DVector');
            } else if (op === 'MULTIPLY') {
                // A is Vector, B is Number -> outputs Vector
                inputA.setCheck('3DVector');
                inputB.setCheck('Number');
                this.setOutput(true, '3DVector');
            } else if (op === 'DOT') {
                // A is Vector, B is Vector -> outputs Number
                inputA.setCheck('3DVector');
                inputB.setCheck('3DVector');
                this.setOutput(true, 'Number');
            } else { // ADD, SUBTRACT, CROSS
                // A is Vector, B is Vector -> outputs Vector
                inputA.setCheck('3DVector');
                inputB.setCheck('3DVector');
                this.setOutput(true, '3DVector');
            }
        }
    };

    // --- Digital Geometry Category ---:/

    Blockly.Blocks['minecraft_action_create_digital_ball'] = {
        init: function() {
            this.appendDummyInput().appendField("Create Digital Ball");
            this.appendValueInput("CENTER")
                .setCheck("3DVector") // Assumes minecraft_vector_3d outputs "3DVector"
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Center");
            this.appendValueInput("RADIUS")
                .setCheck("Number")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Radius");
            this.appendValueInput("BLOCK_TYPE")
                .setCheck("Block") // From your block pickers
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Block Type");
            this.appendValueInput("INNER_RADIUS")
                .setCheck("Number")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Inner Radius (0 for solid)");
            this.setPreviousStatement(true, null);
            this.setNextStatement(true, null);
            this.setColour(65); // A distinct color for these new actions
            this.setTooltip("Creates a digital ball (sphere) of voxels.");
            this.setInputsInline(false); // Better for multiple inputs


        }
    };

    Blockly.Blocks['minecraft_action_create_digital_cube'] = {
        init: function() {
            this.appendDummyInput().appendField("Create Digital Cube");
            this.appendValueInput("CENTER")
                .setCheck("3DVector")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Center");
            this.appendValueInput("SIDE_LENGTH")
                .setCheck("Number")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Side Length");
            this.appendValueInput("ROTATION_MATRIX")
                .setCheck("3DMatrix") // New type for our matrix blocks
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Rotation Matrix");
            this.appendValueInput("BLOCK_TYPE")
                .setCheck("Block")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Block Type");
            this.appendValueInput("INNER_OFFSET_FACTOR")
                .setCheck("Number")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Inner Offset (0=solid, <1 hollow)");
            this.setPreviousStatement(true, null);
            this.setNextStatement(true, null);
            this.setColour(65);
            this.setTooltip("Creates an oriented digital cube of voxels.");
            this.setInputsInline(false);


        }
    };

    Blockly.Blocks['minecraft_action_create_digital_plane'] = {
        init: function() {
            this.appendDummyInput().appendField("Create Digital Plane (Rectangular)"); // Clarified name
            this.appendValueInput("NORMAL")
                .setCheck(["3DVector","3DUnitVector"])
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Normal Vector");
            this.appendValueInput("POINT_ON_PLANE") // This is the plane's reference point
                .setCheck("3DVector")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Plane Reference Point");
            this.appendValueInput("BLOCK_TYPE")
                .setCheck("Block")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Block Type");
            this.appendValueInput("OUTER_RECT_DIMS") // Now mandatory
                .setCheck("2DVector")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Outer Rect Dims (width, length)");
            this.appendValueInput("PLANE_THICKNESS")
                .setCheck("Number")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Thickness (default 1)");
            this.appendValueInput("INNER_RECT_DIMS") // Optional
                .setCheck("2DVector")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Inner Rect Dims (optional)");
            this.appendValueInput("RECT_CENTER_OFFSET") // Optional offset for the rectangle
                .setCheck("3DVector")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Rect Center Offset (from ref. point)");

            this.setPreviousStatement(true, null);
            this.setNextStatement(true, null);
            this.setColour(65);
            this.setTooltip("Creates a finite rectangular digital plane of voxels.");
            this.setInputsInline(false);


        }
    };

    Blockly.Blocks['minecraft_action_create_digital_disc'] = {
        init: function() {
            this.appendDummyInput().appendField("Create Digital Disc/Annulus");
            this.appendValueInput("NORMAL")
                .setCheck("3DVector")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Normal Vector");
            this.appendValueInput("CENTER_POINT") // Center of the disc on the plane
                .setCheck("3DVector")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Disc Center Point");
            this.appendValueInput("OUTER_RADIUS")
                .setCheck("Number")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Outer Radius");
            this.appendValueInput("BLOCK_TYPE")
                .setCheck("Block")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Block Type");
            this.appendValueInput("DISC_THICKNESS")
                .setCheck("Number")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Thickness (default 1)");
            this.appendValueInput("INNER_RADIUS") // For annulus
                .setCheck("Number")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Inner Radius (0 for solid disc)");

            this.setPreviousStatement(true, null);
            this.setNextStatement(true, null);
            this.setColour(65);
            this.setTooltip("Creates a digital disc or annulus (ring) of voxels.");
            this.setInputsInline(false);


        }
    };

    Blockly.Blocks['minecraft_action_create_digital_tube'] = {
        init: function() {
            this.appendDummyInput()
                .appendField("Create Digital Tube");
            this.appendValueInput("POINT1")
                .setCheck("3DVector")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Start Point (p1)");
            this.appendValueInput("POINT2")
                .setCheck("3DVector")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("End Point (p2)");
            this.appendValueInput("OUTER_THICKNESS")
                .setCheck("Number")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Outer Thickness (radius)");
            this.appendValueInput("BLOCK_TYPE")
                .setCheck("Block")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Block Type");
            this.appendValueInput("INNER_THICKNESS")
                .setCheck("Number")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Inner Thickness (0 for solid)");

            this.setPreviousStatement(true, null);
            this.setNextStatement(true, null);
            this.setColour(65); // A distinct color for digital geometry actions
            this.setTooltip("Creates a digital tube (cylinder) between two points.");
            this.setInputsInline(false);


        }
    };

    Blockly.Blocks['minecraft_action_create_digital_line'] = {
        init: function() {
            this.appendDummyInput()
                .appendField("Create Digital Line");
            this.appendValueInput("POINT1")
                .setCheck("3DVector")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Start Point (p1)");
            this.appendValueInput("POINT2")
                .setCheck("3DVector")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("End Point (p2)");
            this.appendValueInput("BLOCK_TYPE")
                .setCheck("Block")
                .setAlign(Blockly.ALIGN_RIGHT)
                .appendField("Block Type");

            this.setPreviousStatement(true, null);
            this.setNextStatement(true, null);
            this.setColour(65); // Color for digital geometry actions
            this.setTooltip("Creates a 1-voxel thick digital line between two points.");
            this.setInputsInline(false);


        }
    };


    // --- World Actions Category

    Blockly.Blocks['minecraft_action_spawn_entity'] = {
      init: function() {
        this.appendDummyInput()
            .appendField("Spawn Entity");
        this.appendValueInput("ENTITY_TYPE")
            .setCheck("Entity") // Accepts blocks that output the "Entity" type
            .setAlign(Blockly.ALIGN_RIGHT)
            .appendField("Entity Type");
        this.appendValueInput("POSITION")
            .setCheck("3DVector")
            .setAlign(Blockly.ALIGN_RIGHT)
            .appendField("at position");

        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(65); // A distinct "action" color
        this.setTooltip("Spawns a specified entity at a given location.");
        this.setInputsInline(false);

      }
    };
}

