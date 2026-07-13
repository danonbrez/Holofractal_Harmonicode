import React from "react";
export type RejectionExpiryViewerProps = { componentId?: string; roleId?: string; subjectRoot?: string; rejectionState?: string; revalidation?: string };
export const RejectionExpiryViewer: React.FC<RejectionExpiryViewerProps> = (props) => <section data-hhs-pass="061"><h3>RejectionExpiryViewer</h3><pre>{JSON.stringify(props, null, 2)}</pre></section>;
export default RejectionExpiryViewer;
