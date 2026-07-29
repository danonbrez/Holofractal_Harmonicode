# HHS Visual IDE Parallel A/B Usability Lab

This harness reproduces the controlled workflow trials used to select the workflow-first global default.

## What it measures

Two interaction variants execute the same validated local artifact builders:

- `A`: object-first baseline with registry, assistant, API controller, and inspector transitions;
- `B`: workflow-first candidate with modality templates, a five-stage plan, focused execution, and evidence context.

The harness records:

- successful task completion;
- scripted action count;
- context-switch count;
- scripted completion time;
- backend artifact-builder time;
- screenshots and step-frame MP4s.

This is a controlled scripted usability trial, not a recruited-human study. Local artifact success is not a canonical VM81 mutation receipt.

## Requirements

```bash
python -m pip install fastapi uvicorn playwright pillow
```

A Chromium executable and `ffmpeg` must be available. The capture script currently uses `/usr/bin/chromium`; change `executable_path` when required by the host.

## Run the interactive lab

From this directory:

```bash
python -m uvicorn server:app --host 127.0.0.1 --port 8765
```

Open examples:

```text
http://127.0.0.1:8765/?variant=A&workflow=code_api
http://127.0.0.1:8765/?variant=B&workflow=code_api
```

Supported benchmark workflows:

```text
code_api
data_dashboard
document_knowledge
image_spatial
```

## Capture one or more parallel A/B trials

```bash
python capture_parallel.py code_api
python capture_parallel.py data_dashboard document_knowledge image_spatial
```

With no workflow arguments, all four run.

The capture runner:

1. executes both local artifact builders;
2. launches two independent Chromium processes in parallel;
3. drives the A and B interaction paths;
4. captures every stable step;
5. writes successful final screenshots;
6. assembles 9-second H.264 MP4 comparisons with `ffmpeg`;
7. records machine-readable metrics.

Generated files are written beneath:

```text
artifacts/capture/
evidence/frames/
evidence/screenshots/
evidence/videos/
evidence/metrics_raw.json
```

## Authority boundary

The harness does not call or mutate the canonical VM81 runtime. It validates executable local artifacts solely for equal-backend A/B comparison. Production UI promotion remains additive to Pass 161 and continues to use the governed HHS APIs and receipt paths.
