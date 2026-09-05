# HHS Constitutional Ethics Contracts

Status: normative draft for repository implementation
Base: `main@c48423901da7173e1a6e8f0190b1acd3a4ca323c`

## 1. Constitutional invariant

Public authority is a fiduciary delegation, not a personal privilege. Every exercise of governmental power MUST be attributable to a lawful public purpose, bounded by constitutional rights, proportionate to the authority actually delegated, reviewable by an institution independent of the actor, and accompanied by a durable receipt sufficient for later public accountability.

No office, agency, intelligence component, police organization, legislature, executive officer, contractor, or automated system is exempt from this membrane.

## 2. Rights and public-duty boundary

1. The people retain constitutional and human rights against the state.
2. A civil servant does not acquire greater substantive authority merely by holding office.
3. While exercising public authority, an official accepts heightened transparency, auditability, conflict-of-interest disclosure, evidence preservation, and accountability obligations.
4. These obligations attach to official conduct and records. They MUST NOT be implemented as unlimited surveillance of an official's unrelated intimate or private life.
5. Secret governmental action is exceptional rather than ordinary. Any temporary secrecy MUST have a defined lawful basis, scope, custodian, expiration/review condition, immutable access receipt, and independent oversight path.
6. No secret or informal body may possess unreviewable governmental authority.

This contract therefore formalizes the intended accountability principle without creating an unlimited power to invade personal privacy.

## 3. Universal civil-service contract

Every person acting under color of public authority MUST:

- identify the lawful authority and public purpose for consequential acts;
- use the least coercive lawful means reasonably sufficient for that purpose;
- preserve material evidence and decision provenance;
- disclose material financial, organizational, familial, or other conflicts through the lawful disclosure channel;
- refuse unlawful orders and preserve a receipt of the refusal;
- provide truthful information to authorized oversight bodies;
- preserve protected whistleblowing channels;
- distinguish official resources, communications, and decisions from private activity;
- submit consequential automated recommendations to attributable human or legally authorized review where required;
- accept investigation and corrective action when the evidentiary record warrants it.

Retaliation for lawful reporting, auditing, testimony, petition, journalism, or protected dissent is a contract violation.

## 4. Coercive-power contract: police and enforcement personnel

The power to stop, search, detain, arrest, injure, or kill carries the highest evidentiary burden in the civil-service membrane.

For any death or serious bodily injury caused by an officer or other state actor:

1. operational authority directly connected to the incident MUST be removed pending an independent review, subject to lawful employment and due-process procedures;
2. the scene, recordings, dispatch data, communications, weapon/force records, witness information, and relevant telemetry MUST be preserved under auditable chain of custody;
3. the incident MUST be investigated by a body institutionally independent from the involved actor's direct command structure;
4. justification MUST be evaluated from evidence against the governing self-defense/use-of-force standard; a bare assertion such as `I feared for my life` or uncertainty about whether a person possessed a weapon is not by itself dispositive evidence of justification;
5. criminal, civil, employment, licensing, training, and policy questions MUST remain analytically distinct;
6. public findings MUST identify the evidence, governing standard, material uncertainties, disposition, and lawful basis for any redaction.

The contract does not presume guilt. It forbids office from substituting for evidentiary review.

## 5. Executive branch contract

The executive exists to execute enacted law and protect the constitutional order, not to create an unreviewable parallel government.

Executive departments and agencies MUST maintain:

- explicit statutory/constitutional authority maps;
- public mission and jurisdiction boundaries;
- signed delegation chains;
- appropriations and expenditure provenance;
- rulemaking and enforcement receipts;
- inspector-general or equivalently independent audit channels;
- conflict and recusal records for consequential decisions;
- classification/secrecy review with expiration or periodic reauthorization;
- machine-readable public accountability records where disclosure is lawful.

Emergency authority MUST be purpose-limited, time-bounded, reviewable, and incapable of silently becoming permanent ordinary authority.

## 6. Legislative contract

Legislators and legislative staff exercise delegated public power and therefore MUST preserve public accountability for official acts, including votes, sponsorship, material amendments, committee actions, public expenditures, and material conflicts.

Legislative oversight MUST not become a mechanism for retaliation, selective impunity, or secret delegation of powers that the legislature itself could not lawfully exercise.

## 7. Judicial and adjudicative contract

Independence protects impartial adjudication; it does not create unaccountability. Judicial and administrative adjudicative systems MUST preserve attributable decisions, recusal/conflict rules, review mechanisms, evidence integrity, and public reasoning to the extent compatible with lawful privacy, safety, jury, juvenile, and sealed-record protections.

## 8. Intelligence and national-security contract

Necessary secrecy does not equal unaccountable authority. Intelligence activity MUST have a lawful predicate, defined target/scope, minimization rules, access logging, retention/deletion rules, independent oversight, and an auditable authorization chain.

Domestic political opposition, journalism, lawful association, protected speech, or criticism of government MUST NOT become predicates for surveillance or coercive action merely because they inconvenience public officials.

## 9. Public oversight: the reciprocal membrane

The government protects the people; the people retain the capacity to audit the government.

HHS MAY support an open-source public accountability ledger for lawfully public governmental records. Such a ledger MUST:

- distinguish allegation, evidence, finding, and adjudicated fact;
- preserve provenance and correction history;
- reject doxxing and unlawful disclosure of protected personal data;
- expose official decision chains, expenditures, conflicts, votes, enforcement events, and oversight findings when legally public;
- permit reproducible citizen, press, academic, inspector, and judicial auditing;
- never assign guilt or punishment solely from an automated score.

## 10. AI and automated-government contract

An AI system used by government is an instrument of delegated authority and inherits the constraints of its operator.

No automated system may create secret law, secretly expand jurisdiction, fabricate evidence, erase provenance, silently alter an official record, or make an irreversible deprivation decision without the review required by law.

Every consequential automated decision MUST expose sufficient provenance to determine: input authority, governing rule/version, material evidence, transformation/decision receipt, responsible public authority, available appeal/review path, and subsequent correction history.

## 11. HHS trinary admission membrane

For repository implementation, every consequential public-authority transition is classified:

- `+1 ADMIT`: authority, evidence, proportionality, provenance, reviewability, and applicable disclosure requirements pass.
- `0 HOLD`: the act is not admitted because material authority/evidence/review information is unresolved; preserve state and seek lawful resolution.
- `-1 REJECT`: the requested transition conflicts with an invariant, exceeds authority, destroys required provenance, retaliates against protected activity, or attempts an unreviewable bypass.

`0` is not permission by delay. `-1` does not erase the attempted act; the rejection itself receives a durable audit receipt.

## 12. Receipt schema

A constitutional-ethics receipt SHOULD minimally bind:

```json
{
  "actor_public_role": "...",
  "authority": {"source": "...", "scope": "..."},
  "public_purpose": "...",
  "action": "...",
  "evidence_refs": [],
  "conflicts_disclosed": [],
  "rights_implicated": [],
  "necessity_proportionality": "...",
  "decision": "+1|0|-1",
  "review": {"independent_path": "...", "appeal_path": "..."},
  "secrecy": {"basis": null, "review_at": null},
  "provenance": {"previous_receipt": "...", "current_receipt": "..."}
}
```

## 13. Non-bypass invariants

The following are forbidden regardless of rank:

- unreceipted exercise of consequential public authority;
- self-authorized exemption from oversight;
- destruction or falsification of material evidence;
- retaliation against lawful oversight or protected reporting;
- secret expansion of jurisdiction;
- conflicts concealed from the legally authorized disclosure/recusal process;
- permanent emergency powers by inertia;
- automated punishment based solely on opaque inference;
- treating institutional affiliation as proof of innocence or guilt.

## 14. Closure condition

A governmental action is constitutionally closed in HHS only when its authority, purpose, evidence, rights impact, decision provenance, review path, and disposition can be reconstructed from repository/ledger-visible receipts subject to lawful privacy and secrecy constraints.

The implementation target is not universal surveillance. It is universal accountability for the exercise of delegated public power.
