import React from "react";
export type LocalRejectionDecisionViewerProps = { componentId?: string; roleId?: string; subjectRoot?: string; rejectionState?: string; revalidation?: string };
export const LocalRejectionDecisionViewer: React.FC<LocalRejectionDecisionViewerProps> = (props) => <section data-hhs-pass="061"><h3>LocalRejectionDecisionViewer</h3><pre>{JSON.stringify(props, null, 2)}</pre></section>;
export default LocalRejectionDecisionViewer;
