import fs from 'fs';
import path from 'path';

// Helper to format names like HOSTILE_MOBS -> "Hostile Mobs"
function generateBlocklyName(id) {
    if (!id || typeof id !== 'string') return '';
    return id.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function generateFiles() {
    let pickersData = {};

    try {
        // Construct the full path to the JSON file
        // __dirname is not available in ES modules by default.
        // A common way to get the current directory in an ES module:
        const currentModuleUrl = new URL(import.meta.url);
        const currentModuleDir = path.dirname(currentModuleUrl.pathname);


        const pickersPath = path.join(currentModuleDir, 'pickers.json');
        const pickersRawData = fs.readFileSync(pickersPath);
        pickersData = JSON.parse(pickersRawData);



    //     console.log("Successfully loaded colourables.json:", colorableData);

    } catch (error) {
        console.error("Error loading data from JSON files:", error);
        // Set to default empty values if loading fails, so the rest of the script can run
        pickersData = {};
    }


    try {
//         console.log(`Loading data from ${inputJsonFile}...`);
//         const pickersData = JSON.parse(fs.readFileSync(inputJsonFile, 'utf8'));

        let blockDefsOutput = `export function defineMinecraftEntityBlocks(Blockly) {\n`;
        let pythonGenOutput = `// Helper for picker blocks (can be shared if in a common scope)\nfunction createPickerGenerator(block, generator, fieldName = 'ENTITY_ID') { const blockId = block.getFieldValue(fieldName); return [\`'\${blockId}'\`, generator.ORDER_ATOMIC]; }\n\nexport function installMCEntityGenerator(pythonGenerator) {\n`;

        console.log(`Found ${Object.keys(pickersData).length} entity picker groups to generate.`);

        let toolboxXmlOutput = `  <category name="Entities" colour="#5b5ba5">\n`; // Start the new category

        // Generate a block for each picker group defined in the JSON
        for (const pickerName in pickersData) {
            const blocklyBlockName = `minecraft_picker_entity_${pickerName.toLowerCase()}`;
            const options = pickersData[pickerName];
            const humanReadablePickerName = generateBlocklyName(pickerName);

            // Format the options for the FieldDropdown constructor
            const dropdownOptionsString = options.map(id => `["${generateBlocklyName(id)}", "${id}"]`).join(',\n                    ');

            // --- Generate the Blockly Block Definition ---
            blockDefsOutput += `
    Blockly.Blocks['${blocklyBlockName}'] = {
        init: function() {
            this.appendDummyInput()
                .appendField("${humanReadablePickerName}")
                .appendField(new Blockly.FieldDropdown([
                    ${dropdownOptionsString}
                ]), "ENTITY_ID"); // Use a consistent field name
            this.setOutput(true, "Entity"); // Output a generic "Entity" type
            this.setColour(260); // A color for entity blocks
            this.setTooltip("Select a ${humanReadablePickerName}.");
        }
    };
`;
            // --- Generate the Python Generator for this new block ---
            pythonGenOutput += `
    pythonGenerator.forBlock['${blocklyBlockName}'] = function(block, generator) {
        return createPickerGenerator(block, generator, 'ENTITY_ID');
    };
`;
            // Add to Toolbox XML
            toolboxXmlOutput += `    <block type="${blocklyBlockName}"></block>\n`;

        }

        // Finalize the output strings
        blockDefsOutput += `\n} // End of defineMinecraftEntityBlocks\n`;
        pythonGenOutput += `\n} // End of installEntityGenerators\n`;
        toolboxXmlOutput += `  </category>`;

        // Write the generated code to files
        // 1. Use `path.join` to construct the full, safe path to the new directory
        const currentModuleUrl = new URL(import.meta.url);
        const currentModuleDir = path.dirname(currentModuleUrl.pathname);

        const directoryPathBlocks = path.join(currentModuleDir, 'blocks'); // Example: creates 'my-new-directory' inside a 'subfolder'
        const directoryPathPython = path.join(currentModuleDir, 'python'); // Example: creates 'my-new-directory' inside a 'subfolder'

        // 2. Use `fs.mkdirSync` to create the directory
        try {
            // The { recursive: true } option is very useful. It's like `mkdir -p` on Linux.
            // - It will create parent directories if they don't exist (e.g., 'subfolder').
            // - It will NOT throw an error if the directory already exists.
            fs.mkdirSync(directoryPathBlocks, { recursive: true });
            fs.mkdirSync(directoryPathPython, { recursive: true });

        } catch (error) {
            console.error(`Error creating directory: ${error.message}`);
        }

        fs.writeFileSync(path.join(directoryPathBlocks,'entities.mjs'), blockDefsOutput, 'utf8');
        console.log("Successfully generated blocks/entities.mjs");
        fs.writeFileSync(path.join(directoryPathPython,'entities.mjs'), pythonGenOutput, 'utf8');
        console.log("Successfully generated python/entities.js");
        fs.writeFileSync(path.join(currentModuleDir,'toolbox.xml'),toolboxXmlOutput, 'utf8');
        console.log("Successfully generated toolbox.xml");


//         // Ensure directories exist
//         fs.mkdirSync(path.dirname(outputBlockDefsFile), { recursive: true });
//         fs.mkdirSync(path.dirname(outputPythonGenFile), { recursive: true });
//
//         // Write the generated code to files
//         fs.writeFileSync(outputBlockDefsFile, blockDefsOutput, 'utf8');
//         console.log(`Successfully generated ${currentModuleDir}/blocks/materials.mjs`);
//         fs.writeFileSync(outputPythonGenFile, pythonGenOutput, 'utf8');
//         console.log(`Successfully generated ${currentModuleDir}/python/entities.mjs`);

    } catch (error) {
        console.error("Failed to generate entity Blockly files:", error);
    }
}

generateFiles();