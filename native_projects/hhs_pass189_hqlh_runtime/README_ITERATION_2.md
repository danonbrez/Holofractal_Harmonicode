# Pass 189 Iteration 2

Iteration 2 adds durable calibration, bounded output admission, atomic worldline batches, and checkpoint recovery to the Pass 189 HQLH runtime.

## Local validation

```sh
make validate
```

## Run the Iteration 2 service

```sh
PYTHONPATH=python python3 server/hhs_pass189_iteration2_server.py \
  --host 127.0.0.1 --port 8190 --db ./state/iteration2.sqlite3
```

Open `http://127.0.0.1:8190/pass189/i2/`.

## Canonical limits

- Floats are rejected from canonical ingress.
- Synthetic calibration never authorizes physical candidates.
- Physical admission requires validated measured evidence, device attestation, and operator arming.
- No device driver or actuator dispatch is included.
- Worldline batches are admitted atomically under one receipt.
- Vercel is not part of deployment authority.
