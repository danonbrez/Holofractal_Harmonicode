export const HASH72_SIZE = 72;
export const PARTICLE_COUNT = HASH72_SIZE * HASH72_SIZE;
export const LO_SHU = Object.freeze([4, 9, 2, 3, 5, 7, 8, 1, 6]);
export const HASH72_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";

const MASK64 = (1n << 64n) - 1n;

function mix64(value) {
  let x = value & MASK64;
  x ^= x >> 33n;
  x = (x * 0xff51afd7ed558ccdn) & MASK64;
  x ^= x >> 33n;
  x = (x * 0xc4ceb9fe1a85ec53n) & MASK64;
  x ^= x >> 33n;
  return x & MASK64;
}

export function hash72String(input) {
  const bytes = new TextEncoder().encode(String(input));
  let state = 0x179971179971n;
  for (let index = 0; index < bytes.length; index += 1) {
    state ^= BigInt(bytes[index]) << BigInt((index % 8) * 8);
    state = mix64(state + BigInt(index + 1));
  }
  let output = "";
  for (let index = 0; index < 72; index += 1) {
    state = mix64(state + 0x517cc1b727220a95n * BigInt(index + 1));
    output += HASH72_ALPHABET[Number(state % 72n)];
  }
  return output;
}

function assertRange(name, value, lower, upperExclusive) {
  if (!Number.isInteger(value) || value < lower || value >= upperExclusive) {
    throw new RangeError(`${name} must be an integer in [${lower}, ${upperExclusive})`);
  }
}

export function pairToLinearIndex(hashStateA, hashStateB) {
  assertRange("hashStateA", hashStateA, 0, HASH72_SIZE);
  assertRange("hashStateB", hashStateB, 0, HASH72_SIZE);
  return HASH72_SIZE * hashStateA + hashStateB;
}

export function reciprocalIndex(hashStateA, hashStateB) {
  return pairToLinearIndex(HASH72_SIZE - 1 - hashStateA, HASH72_SIZE - 1 - hashStateB);
}

export function mapLinearIndex(linearIndex) {
  assertRange("linearIndex", linearIndex, 0, PARTICLE_COUNT);
  const hashStateA = Math.floor(linearIndex / HASH72_SIZE);
  const hashStateB = linearIndex % HASH72_SIZE;
  const sectorA = Math.floor(hashStateA / 9);
  const sectorB = Math.floor(hashStateB / 9);
  const vm81Row = hashStateA % 9;
  const vm81Column = hashStateB % 9;
  const vm81Cell = 9 * vm81Row + vm81Column;
  const record = {
    particle_id: `H72:${hashStateA}:${hashStateB}`,
    linear_index: linearIndex,
    hash_state_a: hashStateA,
    hash_state_b: hashStateB,
    sector_a: sectorA,
    sector_b: sectorB,
    vm81_row: vm81Row,
    vm81_column: vm81Column,
    vm81_cell: vm81Cell,
    loshu_a: LO_SHU[vm81Row],
    loshu_b: LO_SHU[vm81Column],
    reciprocal_index: reciprocalIndex(hashStateA, hashStateB),
    previous_index: (linearIndex + PARTICLE_COUNT - 1) % PARTICLE_COUNT,
    next_index: (linearIndex + 1) % PARTICLE_COUNT,
    phase72: (hashStateA + hashStateB) % 72,
    phase64: (8 * sectorA + sectorB) % 64,
    refresh_phase576: (72 * ((vm81Row + vm81Column) % 8) + ((hashStateA + hashStateB) % 72)) % 576,
    geometry_class: (vm81Cell + sectorA + sectorB) % 4,
    material_class: (LO_SHU[vm81Row] + LO_SHU[vm81Column]) % 9,
    lod_class: "LOD2",
    visibility_class: "VISIBLE",
  };
  return Object.freeze({
    ...record,
    state_hash72: hash72String(JSON.stringify(record)),
  });
}

export function createAddressTable() {
  return Object.freeze(Array.from({ length: PARTICLE_COUNT }, (_, index) => mapLinearIndex(index)));
}

export function validateAddressTable(table) {
  if (!Array.isArray(table) || table.length !== PARTICLE_COUNT) {
    return { valid: false, classification: "PARTICLE_COUNT_MISMATCH" };
  }
  const indices = new Set();
  const pairs = new Set();
  const sectorCells = new Map();
  for (const particle of table) {
    indices.add(particle.linear_index);
    pairs.add(`${particle.hash_state_a}:${particle.hash_state_b}`);
    const sectorKey = `${particle.sector_a}:${particle.sector_b}`;
    if (!sectorCells.has(sectorKey)) sectorCells.set(sectorKey, new Set());
    sectorCells.get(sectorKey).add(particle.vm81_cell);
    if (pairToLinearIndex(particle.hash_state_a, particle.hash_state_b) !== particle.linear_index) {
      return { valid: false, classification: "ADDRESS_INVERSE_MISMATCH", particle };
    }
  }
  const everySectorHasVM81 = sectorCells.size === 64
    && [...sectorCells.values()].every((cells) => cells.size === 81 && [...cells].every((cell) => cell >= 0 && cell < 81));
  return {
    valid: indices.size === PARTICLE_COUNT && pairs.size === PARTICLE_COUNT && everySectorHasVM81,
    classification: indices.size === PARTICLE_COUNT && pairs.size === PARTICLE_COUNT && everySectorHasVM81
      ? "PASS157_PARTICLE_ADDRESS_PROOF_VERIFIED"
      : "PARTICLE_ADDRESS_CONFLICT",
    particle_count: table.length,
    unique_indices: indices.size,
    unique_pairs: pairs.size,
    sector_pairs: sectorCells.size,
    every_sector_has_vm81: everySectorHasVM81,
  };
}
