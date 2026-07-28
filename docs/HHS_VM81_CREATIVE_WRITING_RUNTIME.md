# VM81 Creative-Writing Runtime

## Purpose

The VM81 creative-writing runtime adds a narrow novel-generation API without exposing the language-model provider as an application surface. A caller submits a novel contract to the VM81 runtime; VM81 authorizes the operation, the HHS provider fabric executes bounded text-generation turns, and the HHS persistence guard exports the assembled manuscript into `creative_writing/novels`.

## Authority path

```text
caller
  -> POST /api/runtime/creative/novel
  -> HHS runtime I/O ingress
  -> VM81 authorized tick
  -> HHSAssistantService
       -> provider execution proposal
       -> proposal validation
       -> capability policy gate
       -> LiteRT-LM accelerated transport
       -> provider invocation receipt
       -> provider-result ingress
       -> Hash72 message/turn roots
  -> deterministic manuscript assembly
  -> HHS persistence guard egress
  -> creative_writing/novels/<filename>.md
  -> HHS runtime I/O egress
```

No public route in this implementation accepts a LiteRT-LM base URL, calls `/v1/chat/completions`, or writes model output directly to the filesystem. The only external generation client included in the pass uses the VM81 route.

## API

### Status

```http
GET /api/runtime/creative/novel/status
```

Reports the model request identity, optimization controls, cache state, external surface, and authority identifier.

### Generate

```http
POST /api/runtime/creative/novel
Content-Type: application/json
```

Example request:

```json
{
  "title": "The Ninth Archive",
  "premise": "In a receipt-bound city, an archivist discovers records of events that have not happened yet.",
  "chapter_count": 9,
  "target_words": 9000,
  "filename": "THE_NINTH_ARCHIVE.md",
  "max_concurrency": 2,
  "persist": true,
  "project_id": "project:creative-writing",
  "request_class": "canonical_full_witness_chain"
}
```

Limits:

- title: 1–160 characters
- premise: 1–8,000 characters
- chapters: 3–24
- target words: 3,000–120,000
- generation concurrency: 1–4
- output filename: one Markdown filename with no directory components
- output root: runtime configured; not caller controlled

## Language-model performance optimizations

### 1. Bounded engine context

`CreativeOptimizedTransport` uses LiteRT-LM's request identity form:

```text
<registry-model-id>,<backend>,<max-engine-tokens>
```

The default creative bound is 8,192 engine tokens and is configurable with `HHS_LITERT_LM_CREATIVE_MAX_ENGINE_TOKENS`. This prevents a general-purpose maximum context from being allocated implicitly for each chapter request.

### 2. Compact single-turn threads

The outline and each chapter receive an isolated HHS conversation thread with a maximum retained history of four messages. Prior generated chapters are not replayed into later chapter prompts. This avoids quadratic prompt growth across a long manuscript.

### 3. Story-bible projection

The complete outline is reduced to a compact JSON story bible containing only continuity-bearing fields. Each chapter receives the shared bible and its own chapter contract, rather than the accumulated manuscript.

### 4. Bounded parallel chapter generation

Independent chapter calls are scheduled with an asynchronous semaphore. The default concurrency is two and the API caps it at four to avoid unbounded GPU memory and provider queue pressure.

### 5. No general assistant tool-schema injection

Creative turns use `HHSAssistantService` rather than the general HHS API tool-loop service. Provider proposal validation, policy gating, invocation receipts, result ingress, and Hash72 message roots remain active, while unrelated read-only HHS tool schemas are omitted from every creative prompt.

### 6. Bounded deterministic prompt cache

A process-local LRU cache keys completions by model request identity, project, prompt, response format, and schema domain. It defaults to 64 entries and prevents repeated deterministic generation contracts from invoking the provider again.

### 7. Low reasoning overhead for prose generation

Creative defaults are separated from the general assistant profile:

```text
max output tokens: 4096
reasoning effort: low
temperature: 0.68
top-p: 0.92
top-k: 40
seed: inherited HHS deterministic seed
```

These remain environment configurable without changing the VM81 API contract.

## Environment controls

```text
HHS_CREATIVE_WRITING_ROOT=creative_writing/novels
HHS_LITERT_LM_CREATIVE_MAX_ENGINE_TOKENS=8192
HHS_LITERT_LM_CREATIVE_MAX_OUTPUT_TOKENS=4096
HHS_LITERT_LM_CREATIVE_TEMPERATURE=0.68
HHS_LITERT_LM_CREATIVE_TOP_P=0.92
HHS_LITERT_LM_CREATIVE_TOP_K=40
HHS_LITERT_LM_CREATIVE_REASONING_EFFORT=low
```

The existing LiteRT-LM controls still select the model, backend, and provider endpoint.

## Receipt semantics

A successful response returns:

- `vm81_authorized_tick`
- runtime ingress and egress records
- provider invocation and provider-result ingress evidence inside each admitted assistant turn
- `outline_root_hash72`
- one `chapter_root_hash72` per chapter
- `novel_root_hash72`
- `result_root_hash72`
- persistence-guard evidence

The API does not claim that provider output is canonical without runtime admission, and the model has no direct filesystem or VM81 mutation authority.

## Validation scope

The pass includes targeted tests for:

- engine-token-bound model request identity
- complete three-chapter generation with a deterministic fake provider
- isolated single-turn threads
- absence of prior chapter replay
- persistence through the injected guarded exporter
- chapter, novel, and result Hash72 roots
- rejection of caller-controlled output roots

A live end-to-end provider run requires `litert-lm serve` and the requested model to be available at the configured HHS provider endpoint.
