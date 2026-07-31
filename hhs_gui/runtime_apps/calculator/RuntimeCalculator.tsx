import React from"react"
import{HHSCalculatorSurface}from"./HHSCalculatorSurface"
export interface RuntimeCalculatorProps{initialExpression?:string}
export const RuntimeCalculator:React.FC<RuntimeCalculatorProps>=({initialExpression})=><HHSCalculatorSurface initialExpression={initialExpression}/>
export default RuntimeCalculator
