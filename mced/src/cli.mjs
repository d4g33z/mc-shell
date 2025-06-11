#!/usr/bin/env node
import * as fs from 'fs';
import * as path from 'path';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers'; // For yargs v17+

// Use import syntax for ES Modules
import * as Blockly from 'blockly';
// Import defineGreetingBlock function from greeting.js
import { defineGreetingBlock } from './blocks/greeting.mjs'; // Adjust path if needed
import { defineGreetingPython } from "./generators/python/greeting.mjs";

// Call the function to define the block, passing in the Blockly object
defineGreetingBlock(Blockly); // <----- Call the function, passing Blockly
defineGreetingPython(Blockly);

// console.log("Blockly Object:",Blockly)
// console.log(Blockly['greeting'])

const argv = yargs(hideBin(process.argv)) // Use hideBin for yargs v17+
    .scriptName("blockly-cli")
    .command('$0 <workspaceFile>', 'Generate code from a Blockly workspace XML file', (yargs) => {
        yargs.positional('workspaceFile', {
            describe: 'Path to the Blockly workspace JSON file (.json)'
        })
    })
    .option('language', {
        alias: 'l',
        describe: 'Target language for code generation (python, javascript)',
        choices: ['python', 'javascript'],
        default: 'python'
    })
    .help()
    .argv;

const workspaceFile = argv.workspaceFile;
const language = argv.language;

async function runBlocklyCommandLine() {
    try {
        const workspaceJsonString = fs.readFileSync(path.resolve(workspaceFile), 'utf8'); // Read JSON file as string
        const workspaceJson = JSON.parse(workspaceJsonString); // Parse JSON string to object
        const workspace = new Blockly.Workspace();

        Blockly.serialization.workspaces.load(workspaceJson,workspace)

        let generatedCode = "";
        if (language === 'python') {
            generatedCode = Blockly.Python.workspaceToCode(workspace);
        } else if (language === 'javascript') {
            generatedCode = Blockly.JavaScript.workspaceToCode(workspace);
        } else {
            console.error("Error: Unsupported language:", language);
            process.exit(1);
        }

        console.log("Generated " + language.toUpperCase() + " Code:\n");
        console.log(generatedCode);

    } catch (error) {
        console.error("Error processing workspace file:", error);
        console.error(error);
        process.exit(1);
    }
}

runBlocklyCommandLine();