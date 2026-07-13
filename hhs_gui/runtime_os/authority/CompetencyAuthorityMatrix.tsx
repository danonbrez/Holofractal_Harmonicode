import React from "react";
export type Row={component:string;competency:string;authority_scope:string;current_task:string;source_root:string;revalidation:string};
export function CompetencyAuthorityMatrix({rows=[]}:{rows?:Row[]}){return <table data-hhs-surface="PASS_054_COMPETENCY_AUTHORITY_MATRIX"><thead><tr><th>Component</th><th>Competency</th><th>Authority scope</th><th>Current task</th><th>Source root</th><th>Revalidation</th></tr></thead><tbody>{rows.map((r,i)=><tr key={i}><td>{r.component}</td><td>{r.competency}</td><td>{r.authority_scope}</td><td>{r.current_task}</td><td>{r.source_root}</td><td>{r.revalidation}</td></tr>)}</tbody></table>}
export default CompetencyAuthorityMatrix;
