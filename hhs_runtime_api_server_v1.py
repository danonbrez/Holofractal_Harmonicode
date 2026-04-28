@@
 from hhs_runtime.hhs_convergence_packet_v1 import build_convergence_packet
 from hhs_runtime.hhs_agent_patch_planner_v1 import plan_transformation_patch
+from hhs_runtime.hhs_audio_phase_transport_encoder_v1 import encode_expression_to_wav_stems
@@
 class ConvergencePacketRequest(BaseModel):
     expression: str
     items: List[Dict[str, Any]]
     influences: List[Dict[str, Any]]
+
+
+class AudioEncodeRequest(BaseModel):
+    expression: str
+    items: List[Dict[str, Any]]
@@
 @app.post("/api/agent/plan-patch")
 async def api_plan_patch(req: ConvergencePacketRequest) -> Dict[str, Any]:
     packet = build_convergence_packet(req.expression, req.items, req.influences)
     patch = plan_transformation_patch(packet.to_dict())
     return {"packet": packet.to_dict(), "patch": patch}
+
+
+@app.post("/api/audio/encode")
+async def api_audio_encode(req: AudioEncodeRequest) -> Dict[str, Any]:
+    manifest = encode_expression_to_wav_stems(req.expression, req.items, "demo_reports/audio_phase_transport")
+    return {"manifest": manifest.to_dict()}
