export const DEFAULT_LOD_THRESHOLDS = Object.freeze({
  D01_IN: 12,
  D01_OUT: 15,
  D12_IN: 25,
  D12_OUT: 30,
  D23_IN: 48,
  D23_OUT: 56,
});

export function validateLodThresholds(thresholds = DEFAULT_LOD_THRESHOLDS) {
  const required = ["D01_IN", "D01_OUT", "D12_IN", "D12_OUT", "D23_IN", "D23_OUT"];
  if (required.some((key) => !Number.isFinite(thresholds[key]) || thresholds[key] < 0)) {
    return { valid: false, classification: "INVALID_LOD_THRESHOLDS" };
  }
  const valid = thresholds.D01_IN < thresholds.D01_OUT
    && thresholds.D01_OUT < thresholds.D12_IN
    && thresholds.D12_IN < thresholds.D12_OUT
    && thresholds.D12_OUT < thresholds.D23_IN
    && thresholds.D23_IN < thresholds.D23_OUT;
  return {
    valid,
    classification: valid ? "LOD_HYSTERESIS_VERIFIED" : "INVALID_LOD_THRESHOLDS",
  };
}

export function cameraDistance(position, cameraPosition) {
  if (!Array.isArray(position) || !Array.isArray(cameraPosition) || position.length !== 3 || cameraPosition.length !== 3) {
    throw new TypeError("position and cameraPosition must be three-component arrays");
  }
  const delta = position.map((value, index) => Number(value) - Number(cameraPosition[index]));
  if (delta.some((value) => !Number.isFinite(value))) throw new Error("NONFINITE_PHYSICS_STATE");
  return Math.hypot(...delta);
}

export function selectLod(previousLod, distance, thresholds = DEFAULT_LOD_THRESHOLDS) {
  const proof = validateLodThresholds(thresholds);
  if (!proof.valid) throw new RangeError(proof.classification);
  if (!Number.isFinite(distance) || distance < 0) throw new RangeError("INVALID_CAMERA_DISTANCE");
  switch (previousLod) {
    case "LOD0":
      return distance > thresholds.D01_OUT ? "LOD1" : "LOD0";
    case "LOD1":
      if (distance < thresholds.D01_IN) return "LOD0";
      return distance > thresholds.D12_OUT ? "LOD2" : "LOD1";
    case "LOD2":
      if (distance < thresholds.D12_IN) return "LOD1";
      return distance > thresholds.D23_OUT ? "LOD3" : "LOD2";
    case "LOD3":
      return distance < thresholds.D23_IN ? "LOD2" : "LOD3";
    default:
      if (distance <= thresholds.D01_IN) return "LOD0";
      if (distance <= thresholds.D12_IN) return "LOD1";
      if (distance <= thresholds.D23_IN) return "LOD2";
      return "LOD3";
  }
}
