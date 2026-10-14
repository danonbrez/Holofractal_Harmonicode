"""Exact native/Python Hash216 lineage parity with negative admission tests."""
import ctypes
from hashlib import sha256
from pathlib import Path
import subprocess
from hhs_runtime.core.hash72_validator_v1 import HASH72_ALPHABET
from hhs_runtime.pass219.lane5_penrose8_hash216_loshu_bridge import hash216_lineage_witness

def test_c_native_python_216_coordinate_sha256_parity(tmp_path):
    library=tmp_path/"libhhs_hash216.so"
    subprocess.run(["cc","-std=c11","-O2","-fPIC","-shared",
                    "hhs_runtime/src/hhs_hash216.c","-o",str(library),"-lcrypto"],
                   check=True,timeout=60)
    native=ctypes.CDLL(str(library)).hhs_hash216_lineage_vector_sha256
    native.argtypes=[ctypes.c_char_p]*3+[ctypes.c_void_p,ctypes.c_void_p]
    native.restype=ctypes.c_int
    alphabet=HASH72_ALPHABET
    assert len(alphabet)==72
    vectors=[
        (alphabet,alphabet[::-1],alphabet),
        (alphabet[0]*72,alphabet[1]*72,alphabet[2]*72),
    ]
    for previous,change,receipt in vectors:
        word=ctypes.create_string_buffer(217)
        indexed=ctypes.create_string_buffer(216*64+1)
        assert native(previous.encode(),change.encode(),receipt.encode(),word,indexed)==1
        python=hash216_lineage_witness(previous,change,receipt)
        assert python["status"]=="PASS"
        assert word.value.decode()==python["hash216"]
        assert indexed.value.decode()==python["sha256_vector_concatenated"]
        assert len(indexed.value)==216*64
    assert native(b"%"*72,alphabet.encode(),alphabet.encode(),
                  ctypes.create_string_buffer(217),ctypes.create_string_buffer(216*64+1))==0
    assert native(alphabet[:71].encode(),alphabet.encode(),alphabet.encode(),
                  ctypes.create_string_buffer(217),ctypes.create_string_buffer(216*64+1))==0
