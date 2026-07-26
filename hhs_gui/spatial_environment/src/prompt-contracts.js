export const V1_SCOPE = Object.freeze({
  id: "HHS_GUI_V1_SINGLE_JOURNEY",
  journey: "launch_gui -> runtime.api.command -> deterministic_receipt_observation",
  authorityBoundary: "PROJECTION_AND_ORCHESTRATION_ONLY",
  successCriteria: Object.freeze({
    commandCompletionRate: 1,
    requiredRuntimeSignals: ["step", "state", "receipt"],
    maxPromptRetriesPerContract: 1
  })
});

export const V1_PROMPT_CONTRACTS = Object.freeze([
  Object.freeze({
    id: "prompt.runtime.state.observe",
    developerPrompt: "Get current runtime state and return deterministic status with receipt witness.",
    runtimePrompt: "Execute runtime.state and expose step, state, and receipt indicators.",
    expectedCalls: Object.freeze([
      Object.freeze({ command: "state", args: {} })
    ]),
    expectedSignals: Object.freeze(["step", "state"])
  }),
  Object.freeze({
    id: "prompt.runtime.step.then.observe",
    developerPrompt: "Advance runtime one deterministic step then report resulting state.",
    runtimePrompt: "Execute runtime.step then runtime.state; keep backend authority unchanged.",
    expectedCalls: Object.freeze([
      Object.freeze({ command: "step", args: { body: { steps: 1 } } }),
      Object.freeze({ command: "state", args: {} })
    ]),
    expectedSignals: Object.freeze(["step", "state"])
  }),
  Object.freeze({
    id: "prompt.runtime.receipt.check",
    developerPrompt: "Commit receipt and report receipt continuity witness for replayability.",
    runtimePrompt: "Execute runtime.commit then runtime.state and include receipt reference if present.",
    expectedCalls: Object.freeze([
      Object.freeze({ command: "commit", args: {} }),
      Object.freeze({ command: "state", args: {} })
    ]),
    expectedSignals: Object.freeze(["state"])
  })
]);

