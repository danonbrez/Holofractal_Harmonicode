"""I088 acceptance-only evidence gate, using explicitly synthetic fixtures.

The suite does not claim or attempt a real production/browser acceptance.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import runpy
import subprocess
import sys
import pytest

PIN="579dbb58f7f9d99419e73cb4d686901e6d123212"
MODULE=runpy.run_path("scripts/verify_production_native_causal_acceptance_579dbb58.py",
                      run_name="i088_test")
verify=MODULE["verify_evidence"]
Refused=MODULE["Refused"]


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True),encoding="utf8")
    return path


def fixture(tmp_path):
    turns=[]
    for i in range(4):
        response="synthetic-fixture-only-native-answer-"+str(i)
        turns.append({
          "generation_path":"NATIVE_CAUSAL_LM_SERIALIZED_BLOCK_STREAM",
          "response_block_count":1,
          "runtime_mutation_admitted":False,
          "causal_generation_failure":None,
          "strict_failures":[],
          "response":response,
          "response_sha256":sha256(response.encode()).hexdigest(),
        })
    native=tmp_path/"native.jsonl"
    native.write_text(json.dumps({
      "schema":"HHS_NATIVE_CHAT_CLI_ACCEPTANCE_V1",
      "ok":True,"prompt_count":4,"distinct_response_count":4,
      "turns":turns,"failures":[]
    })+"\n",encoding="utf8")
    promotion=write(tmp_path/"promotion.json",{
      "candidate_sha":PIN,"runtime_os_bundle_sha":PIN,"outcome":"PROMOTED"})
    system=write(tmp_path/"system.json",{"status":"synthetic-fixture-only"})
    interface=write(tmp_path/"interface.json",{
      "interface":"HHS_VISUAL_RUNTIME_OS_WORKSPACE",
      "legacy_harmonizer_is_public_root":False,
      "asset_root":"/var/lib/hhs/runtime-os/releases/"+PIN})
    services=write(tmp_path/"services.json",{"services":[{"name":"fake-1"},{"name":"fake-2"}]})
    html=tmp_path/"root.html"
    html.write_text("HHS Visual Runtime OS Workspace",encoding="utf8")
    browser=write(tmp_path/"browser.json",{
      "schema":"HHS_DIGITALOCEAN_PUBLIC_FRONTEND_CAPABILITY_BROWSER_ACCEPTANCE_V1",
      "ok":True,"expected_sha":PIN,"base_url":"https://example.invalid",
      "expected_service_count":2,"ignore_https_errors":False,
      "visual_program_registry_ready":True,
      "visual_program_execution_verified":True,
      "assistant_execution_verified":True,
      "assistant_chatbot_two_turn_verified":True,
      "workspace_workbench_execution_verified":True,
      "terminal_websocket_execution_verified":True,
      "console_errors":[],"page_errors":[],"request_failures":[],"http_5xx":[],
    })
    shot=tmp_path/"picture.png"
    shot.write_bytes(b"\x89PNG\r\n\x1a\n"+b"synthetic-fixture-only"*8)
    return dict(native=native,promotion=promotion,public_system=system,
       public_interface=interface,public_services=services,public_html=html,
       browser=browser,screenshot=shot,base_url="https://example.invalid")


def mutate_json(kwargs, key, update):
    obj=json.loads(kwargs[key].read_text(encoding="utf8"))
    update(obj)
    write(kwargs[key],obj)


def test_accepts_only_complete_synthetic_evidence_without_lifting_block(tmp_path):
    kw=fixture(tmp_path)
    receipt=verify(**kw)
    assert receipt["ok"] is True
    assert receipt["release_sha"]==PIN
    assert receipt["service_count"]==2
    assert len(receipt["evidence_sha256"])==8
    assert receipt["release_block_automatically_lifted"] is False
    assert receipt["host_updater_automatically_enabled"] is False
    assert receipt["tls_certificate_validation_required"] is True


@pytest.mark.parametrize("change",[
    "promotion_sha","native_fallback","native_duplicate","native_blocks",
    "native_hash","native_mutation","interface_sha","services_empty",
    "browser_failed","browser_sha","browser_skip_tls",
    "browser_missing_flow","missing_screenshot","http_url",
])
def test_rejects_missing_or_corrupted_stage(tmp_path,change):
    kw=fixture(tmp_path)
    if change=="promotion_sha":
        mutate_json(kw,"promotion",lambda x:x.update(candidate_sha="old"))
    elif change.startswith("native"):
        reports=json.loads(kw["native"].read_text(encoding="utf8"))
        if change=="native_fallback":reports["turns"][0]["generation_path"]="EXACT_SEMANTIC_FALLBACK"
        if change=="native_duplicate":reports["turns"][1]["response"]=reports["turns"][0]["response"]
        if change=="native_blocks":reports["turns"][0]["response_block_count"]=0
        if change=="native_hash":reports["turns"][0]["response_sha256"]="0"*64
        if change=="native_mutation":reports["turns"][0]["runtime_mutation_admitted"]=True
        kw["native"].write_text(json.dumps(reports)+"\n",encoding="utf8")
    elif change=="interface_sha":
        mutate_json(kw,"public_interface",lambda x:x.update(asset_root="/invalid"))
    elif change=="services_empty":
        mutate_json(kw,"public_services",lambda x:x.update(services=[]))
    elif change.startswith("browser"):
        def edit(x):
            if change=="browser_failed":x["ok"]=False
            if change=="browser_sha":x["expected_sha"]="wrong"
            if change=="browser_skip_tls":x["ignore_https_errors"]=True
            if change=="browser_missing_flow":x["assistant_execution_verified"]=False
        mutate_json(kw,"browser",edit)
    elif change=="missing_screenshot":kw["screenshot"].unlink()
    elif change=="http_url":kw["base_url"]="http://example.invalid"
    with pytest.raises((Refused,OSError,KeyError,TypeError,ValueError)):
        verify(**kw)


def test_collector_only_runs_as_explicit_operator_and_does_not_promote():
    path="scripts/collect_production_native_causal_acceptance_579dbb58.sh"
    text=Path(path).read_text(encoding="utf8")
    check=subprocess.run(["bash","-n",path],capture_output=True,text=True)
    assert check.returncode==0,check.stderr
    assert "HHS_I088_OPERATOR_APPROVED" in text
    assert '[[ "$(git -C "$ROOT" rev-parse HEAD)" == "$PIN" ]]' in text
    assert "curl --fail" in text
    assert "HHS_PRODUCTION_BROWSER_IGNORE_HTTPS_ERRORS=0" in text
    assert "--native" in text and "--screenshot" in text
    assert "systemctl " not in text
    assert "git reset" not in text and "git checkout" not in text
    assert "ssh " not in text and "scp " not in text
    assert "curl -k" not in text and "--insecure" not in text


def test_synthetic_receipt_cli_mints_only_after_full_validation(tmp_path):
    kw=fixture(tmp_path)
    outfile=tmp_path/"final.json"
    command=[sys.executable,
             "scripts/verify_production_native_causal_acceptance_579dbb58.py"]
    flags={
      "native": "--native", "promotion": "--promotion",
      "public_system": "--public-system", "public_interface": "--public-interface",
      "public_services": "--public-services", "public_html": "--public-html",
      "browser": "--browser", "screenshot": "--screenshot",
      "base_url": "--base-url",
    }
    for name,flag in flags.items():command.extend([flag,str(kw[name])])
    command.extend(["--output",str(outfile)])
    good=subprocess.run(command,capture_output=True,text=True)
    assert good.returncode==0,good.stderr
    assert json.loads(outfile.read_text())["release_block_automatically_lifted"] is False
    outfile.unlink()
    mutate_json(kw,"browser",lambda x:x.update(ok=False))
    bad=subprocess.run(command,capture_output=True,text=True)
    assert bad.returncode!=0
    assert not outfile.exists()
