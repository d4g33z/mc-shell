/**
 * @license
 * Copyright 2024
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * @fileoverview Generating Python for math blocks.
 */

// Export for use in python.mjs
export function installMathGenerators(pythonGenerator) {

    pythonGenerator.math_number = function (block) {
        // Numeric value.
        let code = String(block.getFieldValue('NUM'));
        return [code, pythonGenerator.ORDER_ATOMIC];
    };

    // pythonGenerator.math_arithmetic = function (block) {
    //     // Basic arithmetic operators, and power.
    //     const OPERATORS = {
    //         'ADD': [' + ', pythonGenerator.ORDER_ADDITIVE],
    //         'MINUS': [' - ', pythonGenerator.ORDER_ADDITIVE],
    //         'MULTIPLY': [' * ', pythonGenerator.ORDER_MULTIPLICATIVE],
    //         'DIVIDE': [' / ', pythonGenerator.ORDER_MULTIPLICATIVE],
    //         'POWER': [' ** ', pythonGenerator.ORDER_EXPONENTIATION],
    //     };
    //     const tuple = OPERATORS[block.getFieldValue('OP')];
    //     const operator = tuple[0];
    //     const order = tuple[1];
    //     const argument0 = pythonGenerator.valueToCode(block, 'A', order) || '0';
    //     const argument1 = pythonGenerator.valueToCode(block, 'B', order) || '0';
    //     const code = argument0 + operator + argument1;
    //     return [code, order];
    //     // In case of 'DIVIDE', division is always real division in
    //     // Python 3.  Use // for floor (integer) division.
    // };

    pythonGenerator.math_single = function (block) {
        // Math operators with single operand.
        const operator = block.getFieldValue('OP');
        let code;
        let arg;
        if (operator === 'NEG') {
            // Negation is a special case given its different operator precedence.
            arg = pythonGenerator.valueToCode(block, 'NUM',
                pythonGenerator.ORDER_UNARY_SIGN) || '0';
            return ['-' + arg, pythonGenerator.ORDER_UNARY_SIGN];
        }
        if (operator === 'SIN' || operator === 'COS' || operator === 'TAN') {
            arg = pythonGenerator.valueToCode(block, 'NUM',
                pythonGenerator.ORDER_MULTIPLICATIVE) || '0';
        } else {
            arg = pythonGenerator.valueToCode(block, 'NUM',
                pythonGenerator.ORDER_NONE) || '0';
        }
        // First, handle cases which generate values that don't need parentheses
        // wrapping the code.
        switch (operator) {
            case 'ABS':
                code = 'abs(' + arg + ')';
                break;
            case 'ROOT':
                code = 'math.sqrt(' + arg + ')';
                break;
            case 'LN':
                code = 'math.log(' + arg + ')';
                break;
            case 'LOG10':
                code = 'math.log10(' + arg + ')';
                break;
            case 'EXP':
                code = 'math.exp(' + arg + ')';
                break;
            case 'POW10':
                code = '10 ** ' + arg;
                break;
            case 'ROUND':
                code = 'round(' + arg + ')';
                break;
            case 'ROUNDUP':
                code = 'math.ceil(' + arg + ')';
                break;
            case 'ROUNDDOWN':
                code = 'math.floor(' + arg + ')';
                break;
            case 'SIN':
                code = 'math.sin(' + arg + ' / 180.0 * math.pi)';
                break;
            case 'COS':
                code = 'math.cos(' + arg + ' / 180.0 * math.pi)';
                break;
            case 'TAN':
                code = 'math.tan(' + arg + ' / 180.0 * math.pi)';
                break;
        }
        if (code) {
            return [code, pythonGenerator.ORDER_FUNCTION_CALL];
        }
        // Second, handle cases which generate values that may need parentheses
        // wrapping the code.
        switch (operator) {
            case 'ASIN':
                code = 'math.asin(' + arg + ') / math.pi * 180';
                break;
            case 'ACOS':
                code = 'math.acos(' + arg + ') / math.pi * 180';
                break;
            case 'ATAN':
                code = 'math.atan(' + arg + ') / math.pi * 180';
                break;
            default:
                throw Error('Unknown math operator: ' + operator);
        }
        return [code, pythonGenerator.ORDER_MULTIPLICATIVE];
    };

      pythonGenerator['math_constant'] = function(block) {
        // Constants: PI, E, the Golden Ratio, sqrt(2), 1/sqrt(2), INFINITY.
        const CONSTANTS = {
          'PI': ['math.pi', pythonGenerator.ORDER_MEMBER],
          'E': ['math.e', pythonGenerator.ORDER_MEMBER],
          'GOLDEN_RATIO': ['(1 + math.sqrt(5)) / 2', pythonGenerator.ORDER_MULTIPLICATIVE],
          'SQRT2': ['math.sqrt(2)', pythonGenerator.ORDER_MEMBER],
          'SQRT1_2': ['math.sqrt(1/2)', pythonGenerator.ORDER_MEMBER],
          'INFINITY': ['float(\'inf\')', pythonGenerator.ORDER_ATOMIC],
        };
        return CONSTANTS[block.getFieldValue('CONSTANT')];
      };

    pythonGenerator['math_number_property'] = function(block) {
      // Check if a number is even, odd, prime, whole, positive, negative,
      // or if it is divisible by certain number. Returns true or false.
      const PROPERTIES = {
        'EVEN': ['', pythonGenerator.ORDER_MULTIPLICATIVE,
            ' % 2 == 0'],
        'ODD': ['', pythonGenerator.ORDER_MULTIPLICATIVE,
            ' % 2 == 1'],
        'WHOLE': ['', pythonGenerator.ORDER_NONE,
            '.is_integer()'],
        'POSITIVE': ['', pythonGenerator.ORDER_RELATIONAL,
            ' > 0'],
        'NEGATIVE': ['', pythonGenerator.ORDER_RELATIONAL,
            ' < 0'],
      };
      const numberToCheck = pythonGenerator.valueToCode(block, 'NUMBER_TO_CHECK',
          pythonGenerator.ORDER_MULTIPLICATIVE);
      const dropdownProperty = block.getFieldValue('PROPERTY');
      let code = numberToCheck;
      const [suffix, order, operator] = PROPERTIES[dropdownProperty];
      code += operator;
      return [code, order];
    };

    pythonGenerator['math_modulo'] = function(block) {
      // Remainder computation.
      const argument0 = pythonGenerator.valueToCode(block, 'DIVIDEND',
          pythonGenerator.ORDER_MULTIPLICATIVE) || '0';
      const argument1 = pythonGenerator.valueToCode(block, 'DIVISOR',
          pythonGenerator.ORDER_MULTIPLICATIVE) || '0';
      const code = argument0 + ' % ' + argument1;
      return [code, pythonGenerator.ORDER_MULTIPLICATIVE];
    };
}