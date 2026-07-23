from copy import deepcopy
import pytest

from hhs_runtime.hhs_pass114_palindromic_decimal_state_v1 import (
    NumeralError,
    NumeralRecoveryContract,
    PalindromicDecimalStateEngine,
    _build_pass113_archive,
    pass114_self_test,
)

@pytest.fixture(scope="module")
def result():
    return pass114_self_test()


def _encoded():
    _, archive, roots = _build_pass113_archive()
    engine = PalindromicDecimalStateEngine()
    contract = NumeralRecoveryContract(20_000_000, 50_000_000, 30_000_000, 1024)
    return engine, engine.encode(archive["archive"], recovery_contract=contract, authority_root_hash72=roots["authority"]), roots


def test_pass114_round_trip_through_pass113(result):
    assert result["status"] == "PASS"
    assert result["pass113_recovery"]["recovery_receipt"]["recovery_status"] == "RECOVERY_VALIDATED"


def test_pass114_exact_palindrome_and_center(result):
    numeral = result["encoded"]["numeral"]
    assert numeral["mantissa"] == numeral["mantissa"][::-1]
    assert numeral["mantissa"].count(".") == 1
    assert numeral["decimal_separator_index"] * 2 + 1 == len(numeral["mantissa"])


def test_pass114_bigint_scientific_tuple_is_exact(result):
    numeral = result["encoded"]["numeral"]
    assert numeral["coefficient_bigint_decimal"].isdigit()
    assert isinstance(numeral["decimal_scale"], int)
    assert numeral["scientific_exponent"] == -numeral["decimal_scale"]


def test_pass114_rejects_corrupted_digit_chunk():
    engine, bundle, roots = _encoded()
    bad = deepcopy(bundle["numeral"])
    bad["digit_chunks"][0]["digits"] = ("1" if bad["digit_chunks"][0]["digits"][0] != "1" else "2") + bad["digit_chunks"][0]["digits"][1:]
    with pytest.raises(NumeralError) as exc:
        engine.recover(bad, available_work_units=50_000_000, available_memory_bytes=30_000_000, revalidate_authority_root_hash72=roots["authority"])
    assert exc.value.code in {"REJECT_NUMERAL_ROOT_MISMATCH", "REJECT_DIGIT_CHUNK_ROOT_MISMATCH"}


def test_pass114_rejects_wrong_authority():
    engine, bundle, _ = _encoded()
    with pytest.raises(NumeralError) as exc:
        engine.recover(bundle["numeral"], available_work_units=50_000_000, available_memory_bytes=30_000_000, revalidate_authority_root_hash72="changed")
    assert exc.value.code == "REJECT_AUTHORITY_REACTIVATION_FROM_STORED_NUMERAL"


def test_pass114_rejects_insufficient_resources():
    engine, bundle, roots = _encoded()
    with pytest.raises(NumeralError) as exc:
        engine.recover(bundle["numeral"], available_work_units=1, available_memory_bytes=1, revalidate_authority_root_hash72=roots["authority"])
    assert exc.value.code == "REJECT_DECIMAL_ENCODING_WITHOUT_RECOVERY_CONTRACT"


def test_pass114_rejects_noncentral_separator_after_re_root():
    engine, bundle, roots = _encoded()
    bad = deepcopy(bundle["numeral"])
    mantissa = bad["mantissa"]
    bad["mantissa"] = "." + mantissa.replace(".", "", 1)
    from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
    bad["numeral_root_hash72"] = _hash("hhs_pass114_numeral_v1", {k: deepcopy(v) for k, v in bad.items() if k != "numeral_root_hash72"})
    with pytest.raises(NumeralError) as exc:
        engine.recover(bad, available_work_units=50_000_000, available_memory_bytes=30_000_000, revalidate_authority_root_hash72=roots["authority"])
    assert exc.value.code == "REJECT_NONCENTRAL_DECIMAL_SEPARATOR"


def test_pass114_service_registered_and_conformance_derived():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    registry = make_default_service_registry()
    service = next(x for x in registry.services() if x["name"] == "runtime.palindromic_decimal_state.pass114")
    assert service["conformance_decision"]["derivation_complete"] is True
    assert "exact_bigint_decimal_required" in service["guards"]
    assert "bidirectional_recovery_required" in service["guards"]
