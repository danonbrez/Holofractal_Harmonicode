// hhs_runtime/include/hhs_transport.h
//
// HHS / HARMONICODE
// Canonical Manifold Transport ABI
//
// Runtime Principle:
//
//   transport
//   =
//   canonical manifold propagation topology
//
// NOT:
//   runtime telemetry
//

#ifndef HHS_TRANSPORT_H
#define HHS_TRANSPORT_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>

#include "hhs_hash216.h"
#include "hhs_receipt.h"

/* ============================================================
 * VERSION
 * ============================================================
 */

#define HHS_TRANSPORT_ABI_VERSION_MAJOR 1
#define HHS_TRANSPORT_ABI_VERSION_MINOR 0
#define HHS_TRANSPORT_ABI_VERSION_PATCH 0

/* ============================================================
 * TRANSPORT FLAGS
 * ============================================================
 */

typedef enum HHSTransportFlags {

    HHS_TRANSPORT_ACTIVE            = 1 << 0,
    HHS_TRANSPORT_SYNCHRONIZED     = 1 << 1,
    HHS_TRANSPORT_CONVERGED        = 1 << 2,
    HHS_TRANSPORT_RECONSTRUCTIBLE  = 1 << 3,
    HHS_TRANSPORT_PHASE_LOCKED     = 1 << 4,
    HHS_TRANSPORT_CONSTRAINT_LOCK  = 1 << 5,
    HHS_TRANSPORT_REPLAYABLE       = 1 << 6,
    HHS_TRANSPORT_CANONICAL        = 1 << 7

} HHSTransportFlags;

/* ============================================================
 * TRANSPORT FLUX
 * ============================================================
 */

typedef struct HHSTransportFlux {

    double transport_flux;
    double orientation_flux;
    double constraint_flux;

} HHSTransportFlux;

/* ============================================================
 * TRANSPORT WITNESS
 * ============================================================
 */

typedef struct HHSTransportWitness {

    uint64_t witness_flags;

    double transport_delta;
    double orientation_delta;
    double constraint_delta;

    HHSHash72 forward_hash72;
    HHSHash72 reciprocal_hash72;

} HHSTransportWitness;

/* ============================================================
 * TRANSPORT STATE
 * ============================================================
 */

typedef struct HHSTransportState {

    uint64_t transport_id;

    uint64_t transport_flags;

    HHSTransportFlux flux;
    HHSTransportWitness witness;

    HHSHash216 topology_hash216;
    HHSHash216 reciprocal_hash216;

    uint8_t converged;
    uint8_t synchronized;
    uint8_t reconstructible;
    uint8_t replayable;

} HHSTransportState;

/* ============================================================
 * TRANSPORT TOPOLOGY
 * ============================================================
 */

typedef struct HHSTransportTopology {

    HHSTransportState state;

    HHSReceipt receipt;

} HHSTransportTopology;

/* ============================================================
 * TRANSPORT API
 * ============================================================
 */

/*
 * Lifecycle
 */

void hhs_transport_init(
    HHSTransportTopology* topology
);

void hhs_transport_clear(
    HHSTransportTopology* topology
);

/*
 * Synchronization
 */

void hhs_transport_synchronize(
    HHSTransportTopology* topology
);

void hhs_transport_converge(
    HHSTransportTopology* topology
);

/*
 * Flux update
 */

void hhs_transport_update_flux(
    HHSTransportTopology* topology,
    double transport_flux,
    double orientation_flux,
    double constraint_flux
);

/*
 * Witness update
 */

void hhs_transport_update_witness(
    HHSTransportTopology* topology,
    uint64_t witness_flags,
    double transport_delta,
    double orientation_delta,
    double constraint_delta
);

/*
 * Topology hashing
 */

void hhs_transport_compute_hash216(
    HHSTransportTopology* topology
);

void hhs_transport_compute_reciprocal(
    HHSTransportTopology* topology
);

/*
 * Status
 */

uint8_t hhs_transport_is_converged(
    const HHSTransportTopology* topology
);

uint8_t hhs_transport_is_synchronized(
    const HHSTransportTopology* topology
);

uint8_t hhs_transport_is_reconstructible(
    const HHSTransportTopology* topology
);

uint8_t hhs_transport_is_replayable(
    const HHSTransportTopology* topology
);

/*
 * Flux access
 */

double hhs_transport_flux(
    const HHSTransportTopology* topology
);

double hhs_orientation_flux(
    const HHSTransportTopology* topology
);

double hhs_constraint_flux(
    const HHSTransportTopology* topology
);

/*
 * Receipt access
 */

const HHSReceipt* hhs_transport_receipt(
    const HHSTransportTopology* topology
);

/*
 * Hash access
 */

const HHSHash216* hhs_transport_hash216(
    const HHSTransportTopology* topology
);

const HHSHash216* hhs_transport_reciprocal_hash216(
    const HHSTransportTopology* topology
);

#ifdef __cplusplus
}
#endif

#endif