import React from "react";
export type RejectionProvenanceInspectorProps = { componentId?: string; roleId?: string; subjectRoot?: string; rejectionState?: string; revalidation?: string };
export const RejectionProvenanceInspector: React.FC<RejectionProvenanceInspectorProps> = (props) => <section data-hhs-pass="061"><h3>RejectionProvenanceInspector</h3><pre>{JSON.stringify(props, null, 2)}</pre></section>;
export default RejectionProvenanceInspector;
