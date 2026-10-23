"""Offline regression: PR-only operator repair, never runs on production."""
from pathlib import Path
import re
import subprocess

PIN="579dbb58f7f9d99419e73cb4d686901e6d123212"
SCRIPT=Path("scripts/production-native-causal-host-repair-579dbb58.sh")
DEPLOY=Path(".github/workflows/digitalocean-production-main.yml")
PROVISION=Path("tools/provision_native_causal_model.py")

def audit(s):
    assert 'PIN="'+PIN+'"' in s
    assert "set -Eeuo pipefail" in s
    checks=[
        '[[ "$(git -C "$APP" rev-parse HEAD)" == "$PIN" ]]',
        "flock -w 30 7",
        "systemctl stop hhs-guarded-update.timer",
        "flock -w 15 8",
        "PROMOTION_RECEIPT=",
        '"$APP/tools/provision_native_causal_model.py" --install',
    ]
    assert [s.index(x) for x in checks]==sorted(s.index(x) for x in checks)
    assert s.count(checks[0])==2
    for x in (
      'r.get("candidate_sha") == sys.argv[2]',
      'r.get("runtime_os_bundle_sha") == sys.argv[2]',
      'r.get("outcome") == "PROMOTED"',
      'assert version("transformers") == "4.57.6"',
      'assert version("torch") == "2.14.1+cpu"',
      'assert torch.version.cuda is None',
      "runuser -u hhs -- env",
      "--acceptance --strict-generation --json",
      "len(turns)==4",
      "len(set(hashes))==4",
      'r.get("distinct_response_count")==4',
      'isinstance(blocks,int) and not isinstance(blocks,bool) and blocks>0',
      'item.get("runtime_mutation_admitted") is False',
      "HHS_CAUSAL_REPAIR_RELEASE_GATE_STILL_BLOCKED_PENDING_HTTPS_CHROMIUM",
    ):
        assert x in s,x
    assert "systemctl start hhs-guarded-update.timer" not in s
    assert "systemctl enable hhs-guarded-update.timer" not in s
    assert not re.search(r"(?m)^\s*git\s+(reset|pull|checkout|push|merge|switch)\b",s)

def test_shell_and_heredoc_syntax_no_host_execution():
    s=SCRIPT.read_text(encoding="utf8")
    result=subprocess.run(["bash","-n",str(SCRIPT)],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    audit(s)
    python_blocks=re.findall(r"<<'PYCODE'\n([\s\S]*?)\nPYCODE",s)
    assert len(python_blocks)==4
    for body in python_blocks:
        compile(body,"<operator-heredoc>","exec")

def test_negative_pin_lock_receipt_and_distinct_hash_mutations():
    s=SCRIPT.read_text(encoding="utf8")
    for changed in (
        s.replace(PIN,"6c452d4abe80eff0c77f58a12b43f2902020b5b1"),
        s.replace("flock -w 15 8","flock -w 0 8"),
        s.replace('r.get("runtime_os_bundle_sha") == sys.argv[2]',"True"),
        s.replace("len(set(hashes))==4","True"),
        s.replace('[[ "$(git -C "$APP" rev-parse HEAD)" == "$PIN" ]]',"true"),
    ):
        try:
            audit(changed)
        except (AssertionError,ValueError):
            continue
        raise AssertionError("dangerous edit escaped fail-closed static regression")

def test_existing_exact_main_and_provisioner_contract():
    a=DEPLOY.read_text(encoding="utf8")
    b=PROVISION.read_text(encoding="utf8")
    for x in (
        "remote_sha=$(git rev-parse origin/main)",
        '"$remote_sha" == "$TARGET_SHA"',
        "Verify public HTTPS Runtime OS is reachable",
        "Verify public frontend capability projection in Chromium",
        "HHS_PRODUCTION_NATIVE_CLI_GENERATIVE_CHAT_VERIFIED=1",
    ):
        assert x in a
    assert '"transformers": "4.57.6"' in b
    assert '"torch": "2.14.1+cpu"' in b
    assert "MODEL_WEIGHT_SHA256 =" in b
