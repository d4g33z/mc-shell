// src/blocks/greeting.mjs

console.log("greeting.js: Start of file execution");

export function defineGreetingBlock(Blockly) { // Export a function, take Blockly as arg

    // console.log("greeting.js: defineGreetingBlock function called, Blockly =", Blockly); // Check Blockly object

    console.log("greeting.js: Inside defineGreetingBlock - About to define Blockly.Blocks['greeting']");

    Blockly.Blocks['greeting'] = {
        init: function() {
            console.log("greeting.js: Inside init() function of Blockly.Blocks['greeting']");
            this.appendDummyInput()
                .appendField("Greeting")
                .appendField("Name:")
                .appendField(new Blockly.FieldTextInput(""), "NAME");
            this.appendValueInput("MESSAGE")
                .setCheck(null)
                .appendField("Message:");
            this.setPreviousStatement(true, null);
            this.setNextStatement(true, null);
            this.setColour(160);
            this.setTooltip("Generates a greeting message.");
            this.setHelpUrl("");
            console.log("greeting.js: init() function COMPLETED for Blockly.Blocks['greeting']");
        }
    };

    console.log("greeting.js: defineGreetingBlock - Blockly.Blocks['greeting'] definition COMPLETED");

} // End of defineGreetingBlock function

console.log("greeting.js: End of file execution");