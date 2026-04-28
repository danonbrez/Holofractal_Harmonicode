// ADD IMPORT
import { topDisplayInfluences } from '../displayPhaseAnalysis';

// INSIDE COMPONENT AFTER itemPhases DECLARATION ADD:
const influences = topDisplayInfluences(calculatorPhases, activePhase, 6);

// INSIDE <Canvas> BEFORE END ADD:
{influences.map((inf, i) => (
  <PhaseLine key={`inf-${inf.id}-${i}`} phases={inf.projectedPhases} color="#00ffaa" opacity={0.45} linewidth={1} />
))}

// OPTIONAL HIGHLIGHT TOP INFLUENCE:
{influences[0] && (
  <PhaseMarker index={influences[0].phaseIndex} color="#00ffaa" scale={0.9} pulse onClick={() => onPhaseSelect?.(influences[0].phaseIndex)} />
)}
