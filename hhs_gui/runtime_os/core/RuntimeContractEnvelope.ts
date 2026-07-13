/**
 * HHS Runtime Contract Envelope
 * ---------------------------------------------------
 * Frontend-side contract adapter for canonical backend envelopes.
 *
 * This module does not create runtime authority. It prevents the GUI from
 * treating loose websocket/API payloads as trusted runtime state unless the
 * payload carries the canonical contract shape emitted by the backend.
 *
 * Runtime authority remains server/kernel side:
 *   HHS Foundational Standards -> Meaning Conservation -> Hash72 u^72 kernel
 *   -> canonical runtime contracts -> guarded runtime services.
 */

export const HHS_CONTRACT_VERSION =
    "HHS_CANONICAL_RUNTIME_CONTRACT_V1"

export const HASH72_LENGTH = 72

export type HHSRuntimeDirection =
    | "INGRESS"
    | "PROPAGATION"
    | "EGRESS"
    | "INTERNAL"

export interface HHSHash72KernelWitness {
    schema: "HHS_HASH72_KERNEL_WITNESS_V1"
    digest: string
    dna: string
    zero_sum?: boolean
    positions?: number[]
    rotation_profile?: number[]
    trace_count?: number
    [key: string]: unknown
}

export interface HHSRuntimeContract {
    schema: string
    contract_version: string
    contract_type: string
    contract_hash72?: string
    payload_hash72?: string
    payload_hash72_kernel_witness?: HHSHash72KernelWitness
    [key: string]: unknown
}

export interface HHSRuntimePacketContract
    extends HHSRuntimeContract {
    contract_type: "runtime_packet"
    direction: HHSRuntimeDirection
    source: string
    payload: Record<string, unknown>
    io_receipt?: Record<string, unknown>
}

export interface HHSAPIResponseContract
    extends HHSRuntimeContract {
    contract_type: "api_response"
    route: string
    method: string
    status: string
    payload: Record<string, unknown>
    io?: Record<string, unknown>
}

export interface HHSContractEnvelope<TPayload = Record<string, unknown>> {
    payload: TPayload
    runtime_contract?: HHSRuntimeContract
    runtime_packet?: HHSRuntimePacketContract
    contract_valid: boolean
    reasons: string[]
}

export function isHash72(value: unknown): value is string {
    return (
        typeof value === "string" &&
        value.length === HASH72_LENGTH
    )
}

export function isKernelWitness(
    value: unknown
): value is HHSHash72KernelWitness {
    const witness = value as HHSHash72KernelWitness | undefined

    return Boolean(
        witness &&
        witness.schema === "HHS_HASH72_KERNEL_WITNESS_V1" &&
        isHash72(witness.digest) &&
        typeof witness.dna === "string" &&
        witness.dna.length === HASH72_LENGTH
    )
}

export function validateRuntimeContract(
    contract: unknown,
    expectedType?: string
): { ok: boolean; reasons: string[] } {
    const reasons: string[] = []
    const candidate = contract as HHSRuntimeContract | undefined

    if (!candidate || typeof candidate !== "object") {
        return {
            ok: false,
            reasons: ["runtime contract missing"]
        }
    }

    if (candidate.contract_version !== HHS_CONTRACT_VERSION) {
        reasons.push("contract_version mismatch")
    }

    if (!candidate.schema) {
        reasons.push("schema missing")
    }

    if (!candidate.contract_type) {
        reasons.push("contract_type missing")
    }

    if (
        expectedType &&
        candidate.contract_type !== expectedType
    ) {
        reasons.push(
            `contract_type mismatch: expected ${expectedType}`
        )
    }

    if (
        candidate.contract_hash72 !== undefined &&
        !isHash72(candidate.contract_hash72)
    ) {
        reasons.push("contract_hash72 is not native Hash72")
    }

    if (
        candidate.payload_hash72 !== undefined &&
        !isHash72(candidate.payload_hash72)
    ) {
        reasons.push("payload_hash72 is not native Hash72")
    }

    if (
        candidate.payload_hash72_kernel_witness !== undefined &&
        !isKernelWitness(candidate.payload_hash72_kernel_witness)
    ) {
        reasons.push("payload_hash72_kernel_witness invalid")
    }

    return {
        ok: reasons.length === 0,
        reasons
    }
}

export function unwrapAPIResponseEnvelope<TPayload = Record<string, unknown>>(
    raw: unknown
): HHSContractEnvelope<TPayload> {
    const obj = (
        raw && typeof raw === "object"
            ? raw as Record<string, unknown>
            : {}
    )

    const runtimeContract =
        obj.runtime_contract as HHSRuntimeContract | undefined

    const validation = validateRuntimeContract(
        runtimeContract,
        "api_response"
    )

    return {
        payload: obj as TPayload,
        runtime_contract: runtimeContract,
        contract_valid: validation.ok,
        reasons: validation.reasons
    }
}

export function unwrapRuntimePacketEnvelope(
    raw: unknown
): HHSContractEnvelope<Record<string, unknown>> {
    const obj = (
        raw && typeof raw === "object"
            ? raw as Record<string, unknown>
            : {}
    )

    const runtimePacket = (
        obj.contract_type === "runtime_packet"
            ? obj
            : obj.runtime_packet
    ) as HHSRuntimePacketContract | undefined

    const validation = validateRuntimeContract(
        runtimePacket,
        "runtime_packet"
    )

    const payload = (
        runtimePacket?.payload &&
        typeof runtimePacket.payload === "object"
            ? runtimePacket.payload
            : obj
    ) as Record<string, unknown>

    return {
        payload,
        runtime_packet: runtimePacket,
        contract_valid: validation.ok,
        reasons: validation.reasons
    }
}
