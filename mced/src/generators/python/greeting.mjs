
export function installGreetingGenerator(pythonGenerator) {
    pythonGenerator.forBlock['greeting'] = function(block, generator) {

        console.log("python_generators.js: pythonGeneratorGreeting function called for block:", block); // Log when generator is called

        const nameValue = block.getFieldValue('NAME'); // Get value from NAME field
        const messageValue = pythonGenerator.valueToCode(block, 'MESSAGE', pythonGenerator.ORDER_ATOMIC); // Get code from MESSAGE input

        console.log("python_generators.js: Extracted values - Name:", nameValue, ", Message Input Code:", messageValue); // Log extracted values

        let code = '';

        if (messageValue) { // Check if there's a message input connected
            code = `def greet_${nameValue}(message):\n`;
            code += `    print(f"Hello, ${nameValue}! {message}")\n\n`;
            code += `greet_${nameValue}(${messageValue})\n`; // Call the greeting function
        } else {
            code = `def greet_${nameValue}():\n`;
            code += `    print(f"Hello, ${nameValue}!")\n\n`;
            code += `greet_${nameValue}()\n`; // Call the greeting function without message
        }

        console.log("python_generators.js: Generated Python code:\n", code); // Log the generated code

        return code; // Return the generated Python code string
    };


}
