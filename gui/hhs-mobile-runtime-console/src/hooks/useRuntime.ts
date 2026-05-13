# `useRuntime.ts` — HHS Runtime Transport Layer

## Recommended File Location

```text
gui/hhs-mobile-runtime-console/src/hooks/useRuntime.ts
```

---

# Purpose

The `useRuntime()` hook is the authoritative frontend transport membrane between the React UI layer and the HHS runtime substrate.

It is responsible for:

* ingress transport
* websocket lifecycle
* runtime telemetry
* receipt streaming
* runtime state synchronization
* witness propagation
* deterministic replay transport

It is NOT responsible for:

* symbolic execution
* algebraic normalization
* invariant enforcement
* receipt generation
* kernel logic
* semantic solving

All authority remains inside the backend runtime.

---

# Architectural Role

```text
React Components
        ↓
useRuntime()
        ↓
Runtime Transport Layer
        ↓
HHS Runtime API / WebSocket
        ↓
Kernel / VM81 / Ledger
```

---

# Recommended Runtime State Model

```ts
export type RuntimeState =
    | 'IDLE'
    | 'ROUTING'
    | 'EXECUTING'
    | 'CLOSURE'
    | 'REJOIN'
    | 'DIVERGENCE'
    | 'ORBIT'
    | 'HALT';
```

---

# Recommended File

```ts
import {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useRef,
    useState,
} from 'react';

/* ============================================================
 * Runtime Types
 * ============================================================ */

export type RuntimeState =
    | 'IDLE'
    | 'ROUTING'
    | 'EXECUTING'
    | 'CLOSURE'
    | 'REJOIN'
    | 'DIVERGENCE'
    | 'ORBIT'
    | 'HALT';

export interface RuntimeTelemetry {
    transportFlux: number;
    orientationFlux: number;
    constraintFlux: number;
    entropy: number;
}

export interface RuntimeReceipt {
    hash72: string;
    parent?: string;
    timestamp: number;
    witnesses: string[];
}

export interface RuntimeWitnessFrame {
    witnesses: string[];
}

export interface HHSIntentIngress {
    id: string;
    timestamp: number;

    modality: 'text';

    payload: string;

    origin:
        | 'intent_bar'
        | 'voice_ingress'
        | 'vm_terminal'
        | 'api'
        | 'replay_engine';

    requested_mode?:
        | 'symbolic'
        | 'runtime'
        | 'trace'
        | 'receipt'
        | 'graph'
        | 'adaptive';

    parent_receipt?: string;
}

/* ============================================================
 * Runtime Context
 * ============================================================ */

interface RuntimeContextValue {
    runtimeState: RuntimeState;

    telemetry: RuntimeTelemetry;

    activeReceipt: RuntimeReceipt | null;

    witnesses: string[];

    connected: boolean;

    router: {
        routeIntent: (
            packet: HHSIntentIngress
        ) => Promise<void>;
    };
}

const RuntimeContext = createContext<
    RuntimeContextValue | undefined
>(undefined);

/* ============================================================
 * Provider
 * ============================================================ */

export const RuntimeProvider: React.FC<{
    children: React.ReactNode;
}> = ({ children }) => {

    const socketRef = useRef<WebSocket | null>(null);

    const [connected, setConnected] = useState(false);

    const [runtimeState, setRuntimeState] =
        useState<RuntimeState>('IDLE');

    const [telemetry, setTelemetry] =
        useState<RuntimeTelemetry>({
            transportFlux: 0,
            orientationFlux: 0,
            constraintFlux: 0,
            entropy: 0,
        });

    const [activeReceipt, setActiveReceipt] =
        useState<RuntimeReceipt | null>(null);

    const [witnesses, setWitnesses] =
        useState<string[]>([]);

    /* ========================================================
     * WebSocket Initialization
     * ======================================================== */

    useEffect(() => {

        const socket = new WebSocket(
            'ws://localhost:8000/ws/hhs'
        );

        socketRef.current = socket;

        socket.onopen = () => {
            setConnected(true);
        };

        socket.onclose = () => {
            setConnected(false);
        };

        socket.onerror = (err) => {
            console.error('[HHS::Socket]', err);
        };

        socket.onmessage = (event) => {

            try {

                const data = JSON.parse(event.data);

                switch (data.type) {

                    case 'runtime_state': {
                        setRuntimeState(data.state);
                        break;
                    }

                    case 'telemetry': {
                        setTelemetry(data.payload);
                        break;
                    }

                    case 'receipt': {
                        setActiveReceipt(data.payload);
                        break;
                    }

                    case 'witnesses': {
                        setWitnesses(data.payload.witnesses);
                        break;
                    }

                    case 'orbit_detected': {
                        setRuntimeState('ORBIT');
                        break;
                    }

                    case 'divergence': {
                        setRuntimeState('DIVERGENCE');
                        break;
                    }

                    default:
                        break;
                }

            } catch (err) {
                console.error('[HHS::MessageParse]', err);
            }

        };

        return () => {
            socket.close();
        };

    }, []);

    /* ========================================================
     * Intent Routing
     * ======================================================== */

    const routeIntent = useCallback(
        async (
            packet: HHSIntentIngress
        ) => {

            if (!socketRef.current) {
                throw new Error(
                    'Runtime socket unavailable.'
                );
            }

            setRuntimeState('ROUTING');

            socketRef.current.send(
                JSON.stringify({
                    type: 'intent_ingress',
                    payload: packet,
                })
            );

        },
        []
    );

    /* ========================================================
     * Context Value
     * ======================================================== */

    const value = useMemo<RuntimeContextValue>(() => {

        return {
            runtimeState,
            telemetry,
            activeReceipt,
            witnesses,
            connected,

            router: {
                routeIntent,
            },
        };

    }, [
        runtimeState,
        telemetry,
        activeReceipt,
        witnesses,
        connected,
        routeIntent,
    ]);

    return (
        <RuntimeContext.Provider value={value}>
            {children}
        </RuntimeContext.Provider>
    );

};

/* ============================================================
 * Runtime Hook
 * ============================================================ */

export function useRuntime(): RuntimeContextValue {

    const ctx = useContext(RuntimeContext);

    if (!ctx) {
        throw new Error(
            'useRuntime() must be used inside RuntimeProvider.'
        );
    }

    return ctx;

}
```

---

# Recommended WebSocket Message Topology

## Client → Runtime

```json
{
  "type": "intent_ingress",
  "payload": {
    "id": "uuid",
    "timestamp": 1710000000,
    "payload": "Δe=0",
    "origin": "intent_bar"
  }
}
```

---

## Runtime → Client

### Runtime State

```json
{
  "type": "runtime_state",
  "state": "EXECUTING"
}
```

### Telemetry

```json
{
  "type": "telemetry",
  "payload": {
    "transportFlux": 0.12,
    "orientationFlux": 0.05,
    "constraintFlux": 0.92,
    "entropy": 0.01
  }
}
```

### Receipt

```json
{
  "type": "receipt",
  "payload": {
    "hash72": "0Tf5Ib(jgTm5IPWlg+mtI)",
    "timestamp": 1710000000,
    "witnesses": [
      "W_QGU_APPLIED",
      "W_CLOSE_CONSTRAINT"
    ]
  }
}
```

---

# Important Boundary Rule

The transport layer must remain passive.

The hook may:

```text
stream
route
cache
project
transport
synchronize
```

The hook may NOT:

```text
solve
normalize
enforce
rewrite
collapse symbolic expressions
perform invariant logic
```

The runtime kernel remains the sole authority.

---

# Recommended Adjacent Files

```text
src/
├── hooks/
│   ├── useRuntime.ts
│   ├── useTelemetry.ts
│   └── useReceiptStream.ts
│
├── runtime/
│   ├── websocket.ts
│   ├── router.ts
│   ├── ingress.ts
│   └── receipts.ts
│
├── types/
│   ├── runtime.ts
│   ├── ingress.ts
│   ├── telemetry.ts
│   └── receipts.ts
```

---

# Next Recommended Layer

After `useRuntime.ts`, the next major component should likely be:

```text
RuntimeTelemetry.tsx
```

followed by:

```text
ReceiptStream.tsx
OrbitMap.tsx
DriftVisualizer.tsx
```

Those components complete the transition from:

```text
frontend app
```

into:

```text
runtime observability infrastructure
```
