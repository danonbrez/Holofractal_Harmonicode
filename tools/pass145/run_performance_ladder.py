#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import resource
import tempfile
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.pass145.canonical import canonical_json, hash72
from hhs_runtime.pass145.service import HHS145Service


def run_count(count: int, *, analyze: bool) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"hhs145_perf_{count}_") as td:
        db_path = Path(td) / "knowledge.sqlite3"
        started = time.perf_counter_ns()
        with HHS145Service(db_path) as service:
            for index in range(count):
                text = (
                    f"Document {index}.\n"
                    f"Symbol T{index} denotes deterministic value {index}.\n"
                    "O denotes the HHS operator. π denotes the circular constant.\n"
                ).encode("utf-8")
                service.ingest_bytes(
                    text,
                    name=f"document-{index:06d}.md",
                    mime_type="text/markdown",
                    namespace="performance",
                    source_kind="PERFORMANCE_WORKLOAD",
                    acquisition={"method": "GENERATED_TEST_CORPUS", "index": index},
                    analyze=analyze,
                )
            elapsed_ns = time.perf_counter_ns() - started
            status = service.status()
            db_bytes = db_path.stat().st_size
            report = {
                "schema": "HHS_PASS145_PERFORMANCE_SAMPLE_V1",
                "document_count": count,
                "analyze": analyze,
                "source_bytes": int(service.db.conn.execute("SELECT COALESCE(SUM(byte_length),0) FROM sources").fetchone()[0]),
                "parsed_segments": status["counts"]["segments"],
                "extracted_objects": status["counts"]["objects"],
                "graph_edges": status["counts"]["relations"],
                "validation_count": status["counts"]["validations"],
                "receipt_count": status["counts"]["receipts"],
                "transaction_count": status["counts"]["transactions"],
                "database_bytes": db_bytes,
                "elapsed_ns": elapsed_ns,
                "elapsed_seconds_decimal": f"{elapsed_ns // 1_000_000_000}.{elapsed_ns % 1_000_000_000:09d}",
                "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "database_integrity": status["integrity"]["ok"],
                "receipt_chain_valid": status["receipt_chain"]["ok"],
                "continuation_count": 0,
                "bounded_outcomes": [],
            }
            report["sample_hash72"] = hash72("hhs_pass145_performance_sample_v1", report)
            return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--counts", default="1,9,81")
    parser.add_argument("--no-analyze", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    counts = [int(x) for x in args.counts.split(",") if x.strip()]
    samples = [run_count(count, analyze=not args.no_analyze) for count in counts]
    result = {
        "schema": "HHS_PASS145_PERFORMANCE_REPORT_V1",
        "platform": "HOST_VALIDATION_ENVIRONMENT_NOT_ANDROID",
        "samples": samples,
        "required_real_device_ladder": [1, 9, 81, 729, 6561],
        "executed_counts": counts,
        "unexecuted_counts": [x for x in [1, 9, 81, 729, 6561] if x not in counts],
        "closure_effect": "REAL_DEVICE_PERFORMANCE_NOT_CLOSED",
    }
    result["report_hash72"] = hash72("hhs_pass145_performance_report_v1", result)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(canonical_json(result) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
