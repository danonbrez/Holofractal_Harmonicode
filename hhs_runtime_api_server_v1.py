@@
 from hhs_runtime.hhs_interpreter_autocorrection_suggestions_v1 import build_autocorrection_suggestions, suggestions_to_training_feedback
 from hhs_runtime.hhs_correction_simulation_overlay_v1 import build_correction_simulation_overlay, overlay_to_training_feedback
 from hhs_runtime.hhs_correction_branch_competition_v1 import compete_correction_branches, branch_frontier_to_training_feedback
 from hhs_runtime.harmonicode_interpreter_v1 import interpret
 from hhs_runtime.harmonicode_constraint_solver_v1 import solve_interpreter_result
+from hhs_runtime.hhs_convergence_packet_v1 import build_convergence_packet
+from hhs_runtime.hhs_agent_patch_planner_v1 import plan_transformation_patch
@@
 class CalculatorEvaluateRequest(BaseModel):
     expression: str
+
+
+class ConvergencePacketRequest(BaseModel):
+    expression: str
+    items: List[Dict[str, Any]]
+    influences: List[Dict[str, Any]]
@@
 @app.post("/api/calculator/evaluate")
 async def api_calculator_evaluate(req: CalculatorEvaluateRequest) -> Dict[str, Any]:
@@
     return {"interpreter": interpreted.to_dict(), "solver": solved.to_dict(), "autocorrections": autocorrections.to_dict(), "autocorrection_feedback": correction_feedback, "correctionSimulation": simulation_overlay.to_dict(), "correction_simulation_feedback": simulation_feedback, "correctionBranchFrontier": branch_frontier.to_dict(), "correction_branch_feedback": branch_feedback, "result_hash72": result_hash}
+
+
+@app.post("/api/agent/convergence-packet")
+async def api_build_convergence_packet(req: ConvergencePacketRequest) -> Dict[str, Any]:
+    packet = build_convergence_packet(req.expression, req.items, req.influences)
+    return packet.to_dict()
+
+
+@app.post("/api/agent/plan-patch")
+async def api_plan_patch(req: ConvergencePacketRequest) -> Dict[str, Any]:
+    packet = build_convergence_packet(req.expression, req.items, req.influences)
+    patch = plan_transformation_patch(packet.to_dict())
+    return {"packet": packet.to_dict(), "patch": patch}
