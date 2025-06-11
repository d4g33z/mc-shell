export function defineMathJavaScript(Blockly) {
    Blockly.JavaScript.math_min_max = (t => {
        let e = Blockly.JavaScript.valueToCode(t, "ARG1") || 0, i = Blockly.JavaScript.valueToCode(t, "ARG2") || 0;
        return [`Math.${t.getFieldValue("MINMAX") || "min"}(${e}, ${i})`]
    });

    Blockly.JavaScript.math_max = (t => [
        `Math.max(${Blockly.JavaScript.valueToCode(t, "ARG1") || 0}, ${Blockly.JavaScript.valueToCode(t, "ARG2") || 0})`]);

    Blockly.JavaScript.math_min = (t => [
        `Math.min(${Blockly.JavaScript.valueToCode(t, "ARG1") || 0}, ${Blockly.JavaScript.valueToCode(t, "ARG2") || 0})`]);

    Blockly.JavaScript.math_sign = (t => [
        `math.sign(${Blockly.JavaScript.valueToCode(t, "ARG")}})`]);

    Blockly.JavaScript.math_random = (t => [
        `math.random(${Blockly.JavaScript.valueToCode(t, "MIN") || 0}, ${Blockly.JavaScript.valueToCode(t, "MAX") || 0})`]);

    Blockly.JavaScript.math_lerp = (t => [
        `math.lerp(${Blockly.JavaScript.valueToCode(t, "FROM") || 0}, ${Blockly.JavaScript.valueToCode(t, "TO") || 200}, ${Blockly.JavaScript.valueToCode(t, "PERCENT") || 50})`]);

// Blockly.JavaScript.math_arithmetic = (t => {
//     let e, i = {
//             ADD: [" + ", Blockly.JavaScript.ORDER_ADDITION],
//             MINUS: [" - ", Blockly.JavaScript.ORDER_SUBTRACTION],
//             MULTIPLY: [" * ", Blockly.JavaScript.ORDER_MULTIPLICATION],
//             DIVIDE: [" / ", Blockly.JavaScript.ORDER_DIVISION],
//             POWER: [null, Blockly.JavaScript.ORDER_COMMA]
//         }, n = i[t.getFieldValue("OP")], u = n[0], m = n[1], o = Blockly.JavaScript.valueToCode(t, "A", m) || "0",
//         r = Blockly.JavaScript.valueToCode(t, "B", m) || "0";
//     return u == i.DIVIDE[0] && "0" == r && (r = "1"), u ? (e = o + u + r, [e, m]) : (e = "Math.pow(" + o + ", " + r + ")", [e, Blockly.JavaScript.ORDER_FUNCTION_CALL])
// });
//
// Blockly.JavaScript.unary = (t => {
//     let e, i = t.getFieldValue("LEFT_HAND"), n = t.getFieldValue("OPERATOR") || "+=",
//         u = Blockly.JavaScript.valueToCode(t, "RIGHT_HAND");
//     return u = -1 !== ["/=", "*="].indexOf(n) ? u || 1 : u || 0, e = `${i} ${n} ${u};\n`
// });
}
