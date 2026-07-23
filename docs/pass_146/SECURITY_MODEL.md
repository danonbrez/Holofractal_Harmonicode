# Pass 146 Security Model

## Identity credentials

Authentication tokens are returned once. The database stores a scrypt verifier, not the plaintext token. Each identity also owns an Ed25519 signing key. The private key is encrypted with AES-256-GCM under a scrypt-derived key and cannot be unlocked without the identity token. Receipts and public records expose only the public key and its SHA-256 fingerprint.

## Signed propagation

A `PROPAGATE` path creates a `HHS_PASS146_SIGNED_PROPAGATION_UNIT_V2` envelope containing:

- exact data and Hash72 data identity;
- provenance;
- sender identity and grant witness;
- boundary contract and path witness;
- disclosure scope;
- expected destination state;
- reversibility metadata;
- source and destination peers;
- sender Ed25519 public key and fingerprint;
- envelope Hash72 root;
- Ed25519 signature;
- signed message Hash72 root.

The receiving node must already contain an explicit peer-trust record matching the public key, classification, and destination. It validates the signed envelope before a receiving boundary is instantiated, then constructs and executes an independent `RECEIVE_PROPAGATION` path.

## No ambient trust

Connected, trusted, authenticated, valid, and authorized are separate states. Trusting a sender key does not grant database mutation, broader disclosure, or arbitrary destination access.

## Key limitation

The tested transport binds only to loopback. Remote binding remains prohibited until certificate identity, remote authentication, revocation, network threat tests, Android packaging, and physical multi-device execution are implemented and evidenced.
