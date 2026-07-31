export type CalculatorAngleMode="DEG"|"RAD"|"GRAD"
export type CalculatorDisplayMode="AUTO"|"DECIMAL"|"FRACTION"
export interface CalculatorEvaluation{input:string;normalized:string;value:number|boolean;decimal:string;fraction:string;symbolic:string|null;display:string;variables:Record<string,number>}
export interface CalculatorEvaluationOptions{angleMode?:CalculatorAngleMode;displayMode?:CalculatorDisplayMode;variables?:Record<string,number>;ans?:number;precision?:number;maxIterations?:number}
export class CalculatorSyntaxError extends Error{position:number}
export function evaluateScientificExpression(expression:string,options?:CalculatorEvaluationOptions):CalculatorEvaluation
export function formatCalculatorNumber(value:number|boolean,options?:{displayMode?:"FRACTION";precision?:number;maxDenominator?:number}):string
export function calculatorCapabilities():{constants:string[];functions:string[];operators:string[];angleModes:CalculatorAngleMode[];exactSymbols:string[]}
