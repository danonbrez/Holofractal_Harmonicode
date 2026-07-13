import React from "react";
export type RejectionRoleContractInspectorProps = { componentId?: string; roleId?: string; subjectRoot?: string; rejectionState?: string; revalidation?: string };
export const RejectionRoleContractInspector: React.FC<RejectionRoleContractInspectorProps> = (props) => <section data-hhs-pass="061"><h3>RejectionRoleContractInspector</h3><pre>{JSON.stringify(props, null, 2)}</pre></section>;
export default RejectionRoleContractInspector;
