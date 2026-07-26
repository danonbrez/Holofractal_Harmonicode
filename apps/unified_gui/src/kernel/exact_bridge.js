import { hash72String } from "../physics/address_map.js";

function gcd(left, right) {
  let a = left < 0n ? -left : left;
  let b = right < 0n ? -right : right;
  while (b !== 0n) [a, b] = [b, a % b];
  return a;
}

export class ExactRatio {
  constructor(numerator, denominator = 1n) {
    let n = BigInt(numerator);
    let d = BigInt(denominator);
    if (d === 0n) throw new RangeError("ZERO_DENOMINATOR_REQUIRES_TYPED_PHASE_DISPATCH");
    if (d < 0n) {
      n = -n;
      d = -d;
    }
    const divisor = gcd(n, d);
    this.numerator = n / divisor;
    this.denominator = d / divisor;
    Object.freeze(this);
  }

  add(other) {
    const value = ExactRatio.from(other);
    return new ExactRatio(
      this.numerator * value.denominator + value.numerator * this.denominator,
      this.denominator * value.denominator,
    );
  }

  multiply(other) {
    const value = ExactRatio.from(other);
    return new ExactRatio(this.numerator * value.numerator, this.denominator * value.denominator);
  }

  toString() {
    return this.denominator === 1n ? String(this.numerator) : `${this.numerator}/${this.denominator}`;
  }

  static from(value) {
    if (value instanceof ExactRatio) return value;
    if (typeof value === "bigint" || Number.isInteger(value)) return new ExactRatio(value);
    if (typeof value === "string" && /^-?\d+(?:\/\d+)?$/.test(value.trim())) {
      const [numerator, denominator = "1"] = value.trim().split("/");
      return new ExactRatio(BigInt(numerator), BigInt(denominator));
    }
    throw new TypeError("exact ratio input required");
  }
}

export class HHSExactBridge {
  constructor() {
    this.equalities = new Map();
    this.phaseNucleus = Object.freeze({
      pivot_symbol: ".",
      zero_scalar: "0_scalar",
      zero_fold: "0_fold",
      one_scalar: "1_scalar",
      one_renewed: "1_renewed",
      phase_rotation: 72,
      classification: "0_fold .= 1_renewed",
    });
  }

  parse(source) {
    if (typeof source !== "string") throw new TypeError("source must be text");
    const compact = source.replace(/\s+/g, "");
    const nodes = [];
    if (compact.includes("1/0") || compact.includes("0^-1")) {
      nodes.push({ node: "PHASE_RECIPROCAL", dispatch: "PhaseRotate_M_TO_I", source });
    }
    if (compact.includes("u^72")) nodes.push({ node: "PHASE_POWER", base: "u", exponent: 72 });
    if (compact.includes("P^2(MOD)(pq)")) {
      nodes.push({ node: "HHS_MODULAR_NORMALIZATION", authority: "P^2", state: "pq" });
    }
    if (compact.includes("x+y<zw<x<z<yx<wz<y<w<xy")) {
      nodes.push({ node: "CENTER_LINE_PRECEDENCE", operator: "CENTER_LINE_PHASE_PRECEDES" });
    }
    for (const word of ["xy", "yx", "zw", "wz"]) {
      if (compact.includes(word)) nodes.push({ node: "ORDERED_GEAR_WORD", value: word });
    }
    if (source.includes("=") || source.includes("==")) nodes.push({ node: "EQUALITY_MEMBRANE" });
    const result = {
      source,
      nodes,
      source_hash72: hash72String(source),
      classification: nodes.length ? "TYPED_AST_CONSTRUCTED" : "STABLE_UNRESOLVED",
    };
    return Object.freeze(result);
  }

  evaluateExactBinary(left, operator, right) {
    const a = ExactRatio.from(left);
    const b = ExactRatio.from(right);
    if (operator === "+") return a.add(b);
    if (operator === "*") return a.multiply(b);
    throw new Error("INVALID_TYPED_OPERATION");
  }

  registerEquality(identifier, left, right, guard = "EXPLICIT") {
    if (!/^[A-Za-z0-9_.:-]+$/.test(identifier)) throw new Error("INVALID_EQUALITY_IDENTIFIER");
    if (this.equalities.has(identifier)) throw new Error("EQUALITY_ALREADY_REGISTERED");
    const link = Object.freeze({ identifier, left, right, guard, proof_hash72: hash72String(`${left}==${right}|${guard}`) });
    this.equalities.set(identifier, link);
    return link;
  }

  substitute(identifier, source) {
    const link = this.equalities.get(identifier);
    if (!link) throw new Error("SUBSTITUTION_UNAUTHORIZED");
    if (!String(source).includes(link.left)) throw new Error("SUBSTITUTION_TARGET_MISSING");
    const result = String(source).replaceAll(link.left, `(${link.right})`);
    return Object.freeze({ source, result, equality: link, result_hash72: hash72String(result) });
  }

  projectApproximate(value) {
    const ratio = ExactRatio.from(value);
    return Object.freeze({
      exact: ratio.toString(),
      approximate: Number(ratio.numerator) / Number(ratio.denominator),
      authority: "RENDER_ONLY_APPROXIMATION",
    });
  }
}
