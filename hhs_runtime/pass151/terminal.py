from __future__ import annotations
class TerminalClassificationGate:
    def classify(self,obligations:list[dict],native_available:bool,replay_ok:bool,restart_ok:bool,packaged:bool,inherited_blockers:list[str])->dict:
        active=[o["obligation_id"] for o in obligations if o.get("state") not in {"VERIFIED","NOT_APPLICABLE_PROVED","SUPERSEDED_EXPLICITLY"}]
        if active: subsystem="PASS_151_INCOMPLETE"
        elif not native_available: subsystem="PASS_151_NATIVE_VALIDATION_UNAVAILABLE"
        elif not replay_ok: subsystem="PASS_151_REPLAY_MISMATCH"
        elif not restart_ok or not packaged: subsystem="PASS_151_ARTIFACT_PACKAGING_FAILED"
        else: subsystem="PASS_151_INTERNAL_LANGUAGE_PROCESSING_LAYERS_VERIFIED"
        overall=subsystem if not inherited_blockers and subsystem=="PASS_151_INTERNAL_LANGUAGE_PROCESSING_LAYERS_VERIFIED" else "PASS_151_INHERITED_CERTIFICATION_BLOCKED"
        return {"pass151_subsystem_classification":subsystem,"overall_inherited_nucleus_classification":overall,"unresolved_obligation_ids":active,"inherited_blockers":inherited_blockers}
