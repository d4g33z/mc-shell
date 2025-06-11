// THIS IS NOT NECESSARY; WE USE BUILT IN PYTHON MATH
console.log("math.mjs: Start of file execution");

// import {MCED} from "../lib/utils.mjs"; //Importing here!

export function defineMathBlocks(Blockly) {
    const e = "#ff9800";

    Blockly.Blocks.math_min_max = {
        init: function () {
            let t = {
                id: "math_max",
                colour: e,
                message0: "%3 %1 %2",
                args0: [{type: "input_value", name: "ARG1", check: "Number"}, {
                    type: "input_value", name: "ARG2", check: "Number"
                }, {type: "field_dropdown", name: "MINMAX", options: [["min", "min"], ["max", "max"]]}],
                inputsInline: !0,
                output: "Number"
            };
            this.jsonInit(t)
        }
    };

    Blockly.Blocks.math_max = {
        init: function () {
            let t = {
                id: "math_max",
                colour: e,
                message0: "max %1 %2",
                args0: [{type: "input_value", name: "ARG1", check: "Number"}, {
                    type: "input_value", name: "ARG2", check: "Number"
                }],
                inputsInline: !0,
                output: "Number"
            };
            this.jsonInit(t)
        }
    };

    Blockly.Blocks.math_min = {
        init: function () {
            let t = {
                id: "math_min",
                colour: e,
                message0: "min %1 %2",
                args0: [{type: "input_value", name: "ARG1", check: "Number"}, {
                    type: "input_value", name: "ARG2", check: "Number"
                }],
                inputsInline: !0,
                output: "Number"
            };
            this.jsonInit(t)
        }
    };

    Blockly.Blocks.math_sign = {
        init: function () {
            let t = {
                id: "math_sign",
                colour: e,
                message0: "sign %1",
                args0: [{type: "input_value", name: "ARG", check: "Number"}],
                inputsInline: !0,
                output: "Number"
            };
            this.jsonInit(t)
        }
    };

    Blockly.Blocks.math_random = {
        init: function () {
            let t = {
                id: "math_random",
                colour: e,
                message0: "random number from %1 to %2",
                args0: [{type: "input_value", name: "MIN", check: "Number"}, {
                    type: "input_value", name: "MAX", check: "Number"
                }],
                inputsInline: !0,
                output: "Number"
            };
            this.jsonInit(t)
        }
    };

    Blockly.Blocks.math_lerp = {
        init: function () {
            let t = {
                id: "math_lerp",
                colour: e,
                message0: "lerp from %1 to %2 %% %3",
                args0: [{type: "input_value", name: "FROM", check: "Number"}, {
                    type: "input_value", name: "TO", check: "Number"
                }, {type: "input_value", name: "PERCENT", check: "Number"}],
                inputsInline: !0,
                output: "Number"
            };
            this.jsonInit(t)
        }
    };

    Blockly.Blocks.math_unary = {
        init: function () {
            let t = {
                id: "unary",
                type: 'unary_dropdown',
                message0: "%1 %2 %3",
                args0: [
                    { type: "field_variable", name: "LEFT_HAND", variable: Blockly.Msg.VARIABLES_DEFAULT_NAME},
                    {
                        type: "field_dropdown",
                        name: "OPERATOR",
                        options: [["+=", "+="], ["-=", "-="], ["*=", "*="], ["/=", "/="]]
                    },
                    { type: "input_value", name: "RIGHT_HAND", check: "Number"}
                ],
                inputsInline: !0,
                previousStatement: null,
                nextStatement: null
            };
            this.jsonInit(t)
        }
    };

    // Blockly.Blocks.math_arithmetic = {
    //     init: function () {
    //         this.appendValueInput("A").setCheck("Number");
    //         this.appendDummyInput()
    //             .appendField(new Blockly.FieldCustomDropdown(
    //                 [
    //                     ["%{BKY_MATH_ADDITION_SYMBOL}", "ADD"],
    //                     ["%{BKY_MATH_SUBTRACTION_SYMBOL}", "MINUS"],
    //                     ["%{BKY_MATH_MULTIPLICATION_SYMBOL}", "MULTIPLY"],
    //                     ["%{BKY_MATH_DIVISION_SYMBOL}", "DIVIDE"],
    //                     ["%{BKY_MATH_POWER_SYMBOL}", "POWER"]
    //                 ],
    //                 {
    //                     ADD: "%{BKY_MATH_ADDITION_SYMBOL} add",
    //                     MINUS: "%{BKY_MATH_SUBTRACTION_SYMBOL} substract",
    //                     MULTIPLY: "%{BKY_MATH_MULTIPLICATION_SYMBOL} multiply",
    //                     DIVIDE: "%{BKY_MATH_DIVISION_SYMBOL} divide",
    //                     POWER: "%{BKY_MATH_POWER_SYMBOL} to the power of"
    //         }), "OP");
    //         this.appendValueInput("B").setCheck("Number");
    //         this.setInputsInline(!0);
    //         this.setOutput("Number");
    //         this.setColour(e);
    //         this.setHelpUrl("%{BKY_MATH_ARITHMETIC_HELPURL}");
    //     }
    // };
    //
    // MCED.MakeApps.Blockly.Defaults.upgradeCategoryColours("math", e)
}