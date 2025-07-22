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

    // Blockly.Blocks['minecraft_vector_2d'] = {
    //   init: function() {
    //     this.appendDummyInput()
    //         .appendField("w:") // Or "dim1:", "u:"
    //         .appendField(new Blockly.FieldNumber(0), "W") // Using FieldNumber for direct number input
    //         .appendField(" h:") // Or "dim2:", "v:"
    //         .appendField(new Blockly.FieldNumber(0), "H");
    //     this.setOutput(true, "2DVector"); // Output type
    //     this.setColour(180); // A distinct color for 2D vectors
    //     this.setTooltip("A 2D vector or dimension (width, height/length).");
    //     this.setInputsInline(true); // Keep it compact
    //   }
    // };

    // Blockly.Blocks['minecraft_vector_2d'] = {
    //   init: function() {
    //     this.appendValueInput("W")
    //         .setCheck("Number")
    //         .appendField("Vec2 w"); // Changed label slightly for clarity
    //     this.appendValueInput("H")
    //         .setCheck("Number")
    //         .setAlign(Blockly.ALIGN_RIGHT) // Align the 'h' label to the right
    //         .appendField("h");
    //     this.setOutput(true, "2DVector"); // Output type remains the same
    //     this.setColour(180); // Vector Math color
    //     this.setTooltip("Creates a 2D vector or dimension (width, height/length). Accepts numbers or variables.");
    //     this.setInputsInline(true); // Keep it on one line
    //   }
    // };

    // Blockly.Blocks['minecraft_vector_3d'] = {
    //     init: function () {
    //         if (this.isInFlyout) {
    //             this.appendDummyInput()
    //                 .appendField(Blockly.Msg.MINECRAFT_VECTOR);
    //             this.setOutput(true, "3DVector");
    //             this.setColour(160);
    //         } else {
    //             this.appendDummyInput()
    //                 .appendField("x:")
    //                 .appendField(new Blockly.FieldTextInput("0"), "X")
    //                 .appendField("y:")
    //                 .appendField(new Blockly.FieldTextInput("0"), "Y")
    //                 .appendField("z:")
    //                 .appendField(new Blockly.FieldTextInput("0"), "Z");
    //             this.setOutput(true, "3DVector");
    //             this.setColour(160);
    //         }
    //     }
    // };

    Blockly.Blocks['minecraft_vector_3d'] = {
      init: function() {
        // We no longer need the isInFlyout check, as this design works well everywhere.
        this.appendValueInput("X")
            .setCheck("Number") // This input will only accept blocks that output a Number
            .setAlign(Blockly.ALIGN_RIGHT)
            .appendField("Vec3 x");
        this.appendValueInput("Y")
            .setCheck("Number")
            .setAlign(Blockly.ALIGN_RIGHT)
            .appendField("y");
        this.appendValueInput("Z")
            .setCheck("Number")
            .setAlign(Blockly.ALIGN_RIGHT)
            .appendField("z");

        this.setOutput(true, "3DVector"); // The output type remains the same
        this.setColour(180); // Using the Vector Math color for consistency
        this.setTooltip("Creates a 3D vector from x, y, and z components. Accepts numbers or variables.");
        this.setInputsInline(true); // This keeps the x, y, z inputs on a single line
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
            this.setOutput(true, "3DVector");
            this.setColour(160);
        }
    };

    Blockly.Blocks['minecraft_position_get_compass_direction'] = {
      init: function() {
        this.appendDummyInput()
            .appendField("player compass direction");
        this.setOutput(true, "String"); // This block returns a String (e.g., "N", "SW")
        this.setColour(160); // The "Position" category color
        this.setTooltip("Returns the cardinal or intercardinal direction the player is facing (N, NE, E, SE, S, SW, W, NW).");
      }
    };

    // --- Vector Math Category ---:/

    // Blockly.Blocks['minecraft_vector_arithmetic'] = {
    //     init: function() {
    //         this.appendValueInput("A")
    //             .setCheck(["3DVector", "3DMatrix"]); // Input A can be a Vector or Matrix now
    //         this.appendDummyInput()
    //             .appendField(new Blockly.FieldDropdown([
    //                 ["+", "ADD"],
    //                 ["-", "SUBTRACT"],
    //                 ["× (scalar)", "MULTIPLY"],
    //                 ["• (dot product)", "DOT"],
    //                 ["× (cross product)", "CROSS"],
    //                 ["Rotated by Matrix", "MATRIX_MULTIPLY"] // <-- NEW OPERATION ADDED
    //             ]), "OP");
    //         this.appendValueInput("B")
    //             .setCheck(["3DVector", "Number"]);
    //         this.setInputsInline(true);
    //         this.setOutput(true, ["3DVector", "Number"]);
    //         this.setColour(180);
    //         this.setTooltip(() => { // Dynamic tooltip
    //             const op = this.getFieldValue('OP');
    //             const tooltips = {
    //                 'ADD': 'Returns the sum of two vectors.',
    //                 'SUBTRACT': 'Returns the difference of two vectors.',
    //                 'MULTIPLY': 'Returns the vector multiplied by a scalar.',
    //                 'DOT': 'Returns the dot product of two vectors (a number).',
    //                 'CROSS': 'Returns the cross product of two vectors (a new vector perpendicular to both).',
    //                 'MATRIX_MULTIPLY': 'Returns a new vector by transforming a vector with a rotation matrix.'
    //             };
    //             return tooltips[op] || 'Performs vector arithmetic.';
    //         });
    //         this.setHelpUrl("");
    //
    //         MCED.BlocklyUtils.configureShadow(this,"A");
    //         MCED.BlocklyUtils.configureShadow(this,"B");
    //     },
    //
    //     onchange: function(event) {
    //         // Only run on user-made changes to the operator field
    //         if (event.type !== Blockly.Events.BLOCK_CHANGE || event.element !== 'field' || event.name !== 'OP') {
    //             return;
    //         }
    //
    //         const op = this.getFieldValue('OP');
    //         const inputA = this.getInput('A');
    //         const inputB = this.getInput('B');
    //
    //         if (op === 'MATRIX_MULTIPLY') {
    //             // A is Matrix, B is Vector -> outputs Vector
    //             inputA.setCheck('3DMatrix');
    //             inputB.setCheck('3DVector');
    //             this.setOutput(true, '3DVector');
    //         } else if (op === 'MULTIPLY') {
    //             // A is Vector, B is Number -> outputs Vector
    //             inputA.setCheck('3DVector');
    //             inputB.setCheck('Number');
    //             this.setOutput(true, '3DVector');
    //         } else if (op === 'DOT') {
    //             // A is Vector, B is Vector -> outputs Number
    //             inputA.setCheck('3DVector');
    //             inputB.setCheck('3DVector');
    //             this.setOutput(true, 'Number');
    //         } else { // ADD, SUBTRACT, CROSS
    //             // A is Vector, B is Vector -> outputs Vector
    //             inputA.setCheck('3DVector');
    //             inputB.setCheck('3DVector');
    //             this.setOutput(true, '3DVector');
    //         }
    //     }
    // };

    // In src/blocks/mc.mjs

    // Block 1: For operations that take two VECTORS and return a VECTOR (Add, Subtract, Cross Product)
    Blockly.Blocks['minecraft_vector_binary_op'] = {
      init: function() {
        this.appendValueInput("A").setCheck("3DVector");
        this.appendDummyInput()
            .appendField(new Blockly.FieldDropdown([
                ["+", "ADD"],
                ["-", "SUBTRACT"],
                ["× (cross product)", "CROSS"]
            ]), "OP");
        this.appendValueInput("B").setCheck("3DVector");
        this.setInputsInline(true);
        this.setOutput(true, "3DVector");
        this.setColour(180);
        this.setTooltip("Performs vector addition, subtraction, or cross product.");

          MCED.BlocklyUtils.configureShadow(this,"A");
          MCED.BlocklyUtils.configureShadow(this,"B");
      }
    };

    // Block 2: For operations that take a VECTOR and a NUMBER and return a VECTOR (Scalar Multiply)
    Blockly.Blocks['minecraft_vector_scalar_multiply'] = {
      init: function() {
        this.appendValueInput("A").setCheck("3DVector");
        this.appendDummyInput().appendField("×"); // Simple multiplication symbol
        this.appendValueInput("B").setCheck("Number");
        this.setInputsInline(true);
        this.setOutput(true, "3DVector");
        this.setColour(180);
        this.setTooltip("Multiplies a vector by a scalar number.");
          MCED.BlocklyUtils.configureShadow(this,"A");
          MCED.BlocklyUtils.configureShadow(this,"B");
      }
    };

    // Block 3: For operations that take two VECTORS and return a NUMBER (Dot Product)
    Blockly.Blocks['minecraft_vector_dot_product'] = {
      init: function() {
        this.appendValueInput("A").setCheck("3DVector");
        this.appendDummyInput().appendField("• (dot product)");
        this.appendValueInput("B").setCheck("3DVector");
        this.setInputsInline(true);
        this.setOutput(true, "Number"); // Note the different output type
        this.setColour(210); // Use a different color to indicate it returns a Number
        this.setTooltip("Calculates the dot product of two vectors, returning a number.");
          MCED.BlocklyUtils.configureShadow(this,"A");
          MCED.BlocklyUtils.configureShadow(this,"B");
      }
    };

    // Block 4: For Matrix * Vector multiplication
    Blockly.Blocks['minecraft_matrix_vector_multiply'] = {
      init: function() {
        this.appendValueInput("A").setCheck("3DMatrix").appendField("Rotate vector");
        this.appendValueInput("B").setCheck("3DVector").appendField("by matrix");
        this.setInputsInline(true);
        this.setOutput(true, "3DVector");
        this.setColour(180);
        this.setTooltip("Rotates a vector by a transformation matrix.");
          MCED.BlocklyUtils.configureShadow(this,"A");
          MCED.BlocklyUtils.configureShadow(this,"B");
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

            MCED.BlocklyUtils.configureShadow(this, "CENTER");
            MCED.BlocklyUtils.configureShadow(this, "RADIUS");
            MCED.BlocklyUtils.configureShadow(this, "BLOCK_TYPE");
            MCED.BlocklyUtils.configureShadow(this, "INNER_RADIUS");



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

            MCED.BlocklyUtils.configureShadow(this, "CENTER");
            MCED.BlocklyUtils.configureShadow(this, "SIDE_LENGTH");
            MCED.BlocklyUtils.configureShadow(this, "ROTATION_MATRIX");
            MCED.BlocklyUtils.configureShadow(this, "BLOCK_TYPE");
            MCED.BlocklyUtils.configureShadow(this, "INNER_OFFSET_FACTOR");

        }
    };

    Blockly.Blocks['minecraft_action_create_digital_plane'] = {
      init: function() {
        this.appendDummyInput().appendField("Create Digital Plane (Rectangular)");
        this.appendValueInput("NORMAL")
            .setCheck("3DVector")
            .setAlign(Blockly.ALIGN_RIGHT)
            .appendField("Normal Vector");
        this.appendValueInput("POINT_ON_PLANE")
            .setCheck("3DVector")
            .setAlign(Blockly.ALIGN_RIGHT)
            .appendField("Plane Reference Point");
        this.appendValueInput("BLOCK_TYPE")
            .setCheck("Block")
            .setAlign(Blockly.ALIGN_RIGHT)
            .appendField("Block Type");

        // --- THIS IS THE FIX ---
        // Replace the single 2DVector input with two Number inputs.
        this.appendValueInput("OUTER_WIDTH")
            .setCheck("Number")
            .setAlign(Blockly.ALIGN_RIGHT)
            .appendField("Outer Width");
        this.appendValueInput("OUTER_LENGTH")
            .setCheck("Number")
            .setAlign(Blockly.ALIGN_RIGHT)
            .appendField("Outer Length");
        // --- END OF FIX ---

        this.appendValueInput("PLANE_THICKNESS")
            .setCheck("Number")
            .setAlign(Blockly.ALIGN_RIGHT)
            .appendField("Thickness");

        // We can do the same for inner dimensions if needed, or leave it for later.

        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(65);
        this.setTooltip("Creates a finite rectangular digital plane of voxels.");
        this.setInputsInline(false);

        MCED.BlocklyUtils.configureShadow(this, "NORMAL");
        MCED.BlocklyUtils.configureShadow(this, "POINT_ON_PLANE");
        MCED.BlocklyUtils.configureShadow(this, "BLOCK_TYPE");
        MCED.BlocklyUtils.configureShadow(this, "OUTER_WIDTH");
        MCED.BlocklyUtils.configureShadow(this, "OUTER_LENGTH");
        MCED.BlocklyUtils.configureShadow(this, "PLANE_THICKNESS");
      }
    };
    //
    // Blockly.Blocks['minecraft_action_create_digital_plane'] = {
    //     init: function() {
    //         this.appendDummyInput().appendField("Create Digital Plane (Rectangular)"); // Clarified name
    //         this.appendValueInput("NORMAL")
    //             .setCheck(["3DVector","3DUnitVector"])
    //             .setAlign(Blockly.ALIGN_RIGHT)
    //             .appendField("Normal Vector");
    //         this.appendValueInput("POINT_ON_PLANE") // This is the plane's reference point
    //             .setCheck("3DVector")
    //             .setAlign(Blockly.ALIGN_RIGHT)
    //             .appendField("Plane Reference Point");
    //         this.appendValueInput("BLOCK_TYPE")
    //             .setCheck("Block")
    //             .setAlign(Blockly.ALIGN_RIGHT)
    //             .appendField("Block Type");
    //         this.appendValueInput("OUTER_RECT_DIMS") // Now mandatory
    //             .setCheck("2DVector")
    //             .setAlign(Blockly.ALIGN_RIGHT)
    //             .appendField("Outer Rect Dims (width, length)");
    //         this.appendValueInput("PLANE_THICKNESS")
    //             .setCheck("Number")
    //             .setAlign(Blockly.ALIGN_RIGHT)
    //             .appendField("Thickness (default 1)");
    //         this.appendValueInput("INNER_RECT_DIMS") // Optional
    //             .setCheck("2DVector")
    //             .setAlign(Blockly.ALIGN_RIGHT)
    //             .appendField("Inner Rect Dims (optional)");
    //         this.appendValueInput("RECT_CENTER_OFFSET") // Optional offset for the rectangle
    //             .setCheck("3DVector")
    //             .setAlign(Blockly.ALIGN_RIGHT)
    //             .appendField("Rect Center Offset (from ref. point)");
    //
    //         this.setPreviousStatement(true, null);
    //         this.setNextStatement(true, null);
    //         this.setColour(65);
    //         this.setTooltip("Creates a finite rectangular digital plane of voxels.");
    //         this.setInputsInline(false);
    //
    //
    //     }
    // };


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

            MCED.BlocklyUtils.configureShadow(this, "NORMAL");
            MCED.BlocklyUtils.configureShadow(this, "CENTER_POINT");
            MCED.BlocklyUtils.configureShadow(this, "OUTER_RADIUS");
            MCED.BlocklyUtils.configureShadow(this, "BLOCK_TYPE");
            MCED.BlocklyUtils.configureShadow(this, "DISC_THICKNESS");
            MCED.BlocklyUtils.configureShadow(this, "INNER_RADIUS");


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


            MCED.BlocklyUtils.configureShadow(this, "POINT1");
            MCED.BlocklyUtils.configureShadow(this, "POINT2");
            MCED.BlocklyUtils.configureShadow(this, "OUTER_THICKNESS");
            MCED.BlocklyUtils.configureShadow(this, "BLOCK_TYPE");
            MCED.BlocklyUtils.configureShadow(this, "INNER_THICKNESS");
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


            MCED.BlocklyUtils.configureShadow(this, "POINT1");
            MCED.BlocklyUtils.configureShadow(this, "POINT2");
            MCED.BlocklyUtils.configureShadow(this, "BLOCK_TYPE");
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

          MCED.BlocklyUtils.configureShadow(this, "ENTITY_TYPE");
          MCED.BlocklyUtils.configureShadow(this, "POSITION");
      }
    };

    Blockly.Blocks['minecraft_action_set_block'] = {
      init: function() {
        this.appendValueInput("BLOCK_TYPE")
            .setCheck("Block")
            .appendField("set block"); // Label is concise
        this.appendValueInput("POSITION")
            .setCheck("3DVector")
            .setAlign(Blockly.ALIGN_RIGHT)
            .appendField("at");

        this.setPreviousStatement(true, null); // It's an action, so it connects to other statements
        this.setNextStatement(true, null);
        this.setColour(65); // The "action" color
        this.setTooltip("Places a single block at a specified location.");
        this.setInputsInline(true); // Makes the block more compact and readable

          MCED.BlocklyUtils.configureShadow(this, "BLOCK_TYPE");
          MCED.BlocklyUtils.configureShadow(this, "POSITION");
      }
    };

    Blockly.Blocks['minecraft_action_get_block'] = {
      init: function() {
        this.appendValueInput("POSITION")
            .setCheck("3DVector")
            .appendField("get block at");
        this.setOutput(true, "Block"); // This block returns a value of type "Block"
        this.setColour(210); // A different color for "getter" blocks
        this.setTooltip("Gets the type of block at a specific location.");
        this.setInputsInline(true);

        MCED.BlocklyUtils.configureShadow(this, "POSITION");
      }
    };

    Blockly.Blocks['minecraft_action_get_height'] = {
      init: function() {
        this.appendValueInput("POSITION")
            .setCheck("3DVector") // Accepts a 3D vector, but we only use X and Z
            .appendField("get height at (x,z) of");
        this.setOutput(true, "Number"); // This block returns a Number
        this.setColour(210); // "Getter" block color
        this.setTooltip("Gets the Y coordinate of the highest solid block at a given X, Z location.");
        this.setInputsInline(true);

        MCED.BlocklyUtils.configureShadow(this, "POSITION");
      }
    };

    Blockly.Blocks['minecraft_action_post_to_chat'] = {
      init: function() {
        this.appendValueInput("MESSAGE")
            .setCheck("String") // Accepts any block that outputs a string
            .appendField("post to chat");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(65); // The "action" color
        this.setTooltip("Posts a message to the in-game chat.");
        this.setInputsInline(true);

        MCED.BlocklyUtils.configureShadow(this, "MESSAGE");

      }
    };

    Blockly.Blocks['minecraft_action_create_explosion'] = {
      init: function() {
        this.appendValueInput("POSITION")
            .setCheck("3DVector")
            .appendField("create explosion at");
        this.appendValueInput("POWER")
            .setCheck("Number")
            .setAlign(Blockly.ALIGN_RIGHT)
            .appendField("with power");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(65); // The "action" color
        this.setTooltip("Creates an explosion of a specified power at a location. TNT is power 4.");
        this.setInputsInline(true);

          MCED.BlocklyUtils.configureShadow(this,"POSITION");
          MCED.BlocklyUtils.configureShadow(this,"POWER");
      }
    };

    Blockly.Blocks['time_sleep'] = {
        init: function() {
            this.appendValueInput("SECONDS")
                .setCheck("Number")
                .appendField("wait for");
            this.appendDummyInput()
                .appendField("seconds");
            this.setPreviousStatement(true, null);
            this.setNextStatement(true, null);
            this.setColour(120); // A color often used for timing/flow control
            this.setTooltip("Pauses the program for a specified number of seconds.");
            this.setInputsInline(true);
        }
    };
}

