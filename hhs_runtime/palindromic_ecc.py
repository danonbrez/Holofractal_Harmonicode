"""Pass 133.3 exact palindromic SECDED carrier for an encrypted BigInt."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any

from .canonical import (
    CanonicalEncodingError, bigint_to_bytes, bytes_to_bigint, decode_tlv, encode_tlv,
    int_to_min_bytes, min_bytes_to_int, uleb128_encode, uleb128_decode,
)
from .hash72_checkpoint import make_hash72_witness

INNER_MAGIC=b"HHS-P133-CIPHERTEXT\x01"
OUTER_MAGIC=b"HHS-P133-PAL-ECC\x01"
DATA_POS=(3,5,6,7,9,10,11,12)
PARITY_POS=(1,2,4,8)


def _byte_bits(b:int)->list[int]: return [(b>>(7-i))&1 for i in range(8)]
def _bits_byte(bits:list[int])->int:
    out=0
    for bit in bits: out=(out<<1)|bit
    return out


def hamming13_encode_byte(value:int)->list[int]:
    pos=[0]*14
    for p,bit in zip(DATA_POS,_byte_bits(value)): pos[p]=bit
    for p in PARITY_POS:
        parity=0
        for i in range(1,13):
            if i&p and i!=p: parity^=pos[i]
        pos[p]=parity
    overall=0
    for i in range(1,13): overall^=pos[i]
    pos[13]=overall
    return pos[1:]


def hamming13_decode_word(bits:list[int])->tuple[int,str,int|None]:
    if len(bits)!=13 or any(b not in (0,1) for b in bits): raise ValueError("invalid codeword")
    pos=[0]+bits[:]
    syndrome=0
    for p in PARITY_POS:
        parity=0
        for i in range(1,13):
            if i&p: parity^=pos[i]
        if parity: syndrome|=p
    overall=0
    for i in range(1,14): overall^=pos[i]
    corrected=None
    if syndrome and overall:
        if syndrome>12: raise CanonicalEncodingError("invalid SECDED syndrome")
        pos[syndrome]^=1; corrected=syndrome; status="ECC_ERROR_CORRECTED"
    elif not syndrome and overall:
        pos[13]^=1; corrected=13; status="ECC_ERROR_CORRECTED"
    elif syndrome and not overall:
        raise CanonicalEncodingError("ERROR_DETECTED_NOT_CORRECTABLE")
    else: status="NO_ERROR_DETECTED"
    return _bits_byte([pos[p] for p in DATA_POS]),status,corrected


def ecc_encode(data:bytes)->str:
    return ''.join(str(bit) for byte in data for bit in hamming13_encode_byte(byte))


def ecc_decode(bitstring:str)->tuple[bytes,dict[str,Any]]:
    if len(bitstring)%13: raise CanonicalEncodingError("ECC length not divisible by 13")
    out=bytearray(); corrected=[]
    for word_index in range(len(bitstring)//13):
        bits=[int(c) for c in bitstring[word_index*13:(word_index+1)*13]]
        value,status,position=hamming13_decode_word(bits)
        out.append(value)
        if position is not None: corrected.append({"word":word_index,"position":position})
    return bytes(out),{"corrected":corrected,"corrected_count":len(corrected),"status":"ECC_ERROR_CORRECTED" if corrected else "NO_ERROR_DETECTED"}


def _inner_frame(ciphertext:int)->bytes:
    payload=bigint_to_bytes(ciphertext)
    fields=[
        (1,int_to_min_bytes(ciphertext.bit_length())),
        (2,payload),
        (3,sha256(payload).digest()),
        (4,b"HHS-P133-CIPHERTEXT-BIGINT-V1"),
    ]
    return encode_tlv(fields,magic=INNER_MAGIC)


def _decode_inner(raw:bytes)->int:
    f=decode_tlv(raw,magic=INNER_MAGIC)
    if set(f)!={1,2,3,4}: raise CanonicalEncodingError("inner frame fields mismatch")
    if sha256(f[2]).digest()!=f[3]: raise CanonicalEncodingError("ciphertext digest mismatch")
    value=int.from_bytes(f[2],"big")
    if value.bit_length()!=min_bytes_to_int(f[1]): raise CanonicalEncodingError("ciphertext bit length mismatch")
    return value


@dataclass(frozen=True)
class PalindromicCarrier:
    radix:int
    left_bits:str
    center:bytes
    right_bits:str
    ecc_contract:str="SECDED_HAMMING_13_8_T1"

    def validate_shape(self)->None:
        if self.radix!=2: raise CanonicalEncodingError("unsupported radix")
        if self.right_bits!=self.left_bits[::-1]: raise CanonicalEncodingError("MIRROR_ASYMMETRY_DETECTED")
        expected=b"P133-CENTER\x01"+len(self.left_bits).to_bytes(8,"big")
        if self.center!=expected+sha256(expected).digest()[:16]: raise CanonicalEncodingError("PALINDROME_CENTER_CORRUPTED")

    def display(self)->str: return self.left_bits+"."+self.right_bits

    def encode_bytes(self)->bytes:
        self.validate_shape()
        left_int=int(self.left_bits or "0",2)
        right_int=int(self.right_bits or "0",2)
        fields=[
            (1,int_to_min_bytes(self.radix)),(2,int_to_min_bytes(len(self.left_bits))),
            (3,int_to_min_bytes(left_int)),(4,self.center),(5,int_to_min_bytes(right_int)),
            (6,self.ecc_contract.encode()),
        ]
        return encode_tlv(fields,magic=OUTER_MAGIC)

    def to_bigint(self)->int: return bytes_to_bigint(self.encode_bytes())

    @classmethod
    def from_bytes(cls,raw:bytes)->"PalindromicCarrier":
        f=decode_tlv(raw,magic=OUTER_MAGIC)
        if set(f)!={1,2,3,4,5,6}: raise CanonicalEncodingError("outer frame fields mismatch")
        length=min_bytes_to_int(f[2])
        left=format(min_bytes_to_int(f[3]),f"0{length}b")
        right=format(min_bytes_to_int(f[5]),f"0{length}b")
        obj=cls(min_bytes_to_int(f[1]),left,f[4],right,f[6].decode())
        obj.validate_shape(); return obj

    @classmethod
    def from_bigint(cls,value:int)->"PalindromicCarrier": return cls.from_bytes(bigint_to_bytes(value))


def protect_encrypted_bigint(ciphertext:int)->dict[str,Any]:
    inner=_inner_frame(ciphertext)
    left=ecc_encode(inner)
    center_base=b"P133-CENTER\x01"+len(left).to_bytes(8,"big")
    center=center_base+sha256(center_base).digest()[:16]
    carrier=PalindromicCarrier(2,left,center,left[::-1])
    decoded=decode_palindromic_carrier(carrier)
    witness=make_hash72_witness("hhs_pass133_palindromic_ecc_carrier_v1",{
        "radix":2,"left_length":len(left),"center":center.hex(),"carrier_bigint_hex":hex(carrier.to_bigint())
    }).to_dict()
    return {
        "schema":"HHS_PASS133_PALINDROMIC_ECC_BIGINT_CARRIER_V1",
        "status":"PALINDROMIC_ECC_BIGINT_RECONSTRUCTION_VERIFIED" if int(decoded["ciphertext_hex"],16)==ciphertext else "RECONSTRUCTION_VARIANCE_DETECTED",
        "ciphertext_bigint_hex":hex(ciphertext),"carrier_bigint_hex":hex(carrier.to_bigint()),
        "carrier_bit_length":carrier.to_bigint().bit_length(),"radix":2,"half_length":len(left),
        "display_sha256":sha256(carrier.display().encode()).hexdigest(),"center":center.hex(),
        "ecc_contract":carrier.ecc_contract,"correction_capacity_bits_per_codeword":1,
        "decode":decoded,"hash72_witness":witness,
    }


def _decode_half(bits:str)->tuple[int,dict[str,Any]]:
    raw,ecc=ecc_decode(bits)
    return _decode_inner(raw),ecc


def decode_palindromic_carrier(carrier:PalindromicCarrier)->dict[str,Any]:
    mirror_mismatch=carrier.right_bits!=carrier.left_bits[::-1]
    center_ok=True
    try: carrier.validate_shape()
    except CanonicalEncodingError as exc:
        if "MIRROR" not in str(exc): raise
        center_base=b"P133-CENTER\x01"+len(carrier.left_bits).to_bytes(8,"big")
        center_ok=carrier.center==center_base+sha256(center_base).digest()[:16]
    candidates=[]; errors=[]
    for side,bits in (("left",carrier.left_bits),("right",carrier.right_bits[::-1])):
        try:
            value,ecc=_decode_half(bits); candidates.append((side,value,ecc))
        except Exception as exc: errors.append({"side":side,"error":str(exc)})
    values={v for _,v,_ in candidates}
    if len(values)!=1: raise CanonicalEncodingError("AMBIGUOUS_CORRECTION_REJECTED" if len(values)>1 else "ERROR_DETECTED_NOT_CORRECTABLE")
    value=next(iter(values))
    corrections=sum(c[2]["corrected_count"] for c in candidates)
    return {
        "ciphertext_hex":hex(value),"mirror_asymmetry":mirror_mismatch,"center_valid":center_ok,
        "correction_events":corrections,"candidate_sides":[c[0] for c in candidates],"errors":errors,
        "status":"ECC_ERROR_CORRECTED" if corrections else ("MIRROR_ASYMMETRY_DETECTED" if mirror_mismatch else "NO_ERROR_DETECTED")
    }


def run_ecc_stress(ciphertext:int, sample_limit:int=256)->dict[str,Any]:
    base=protect_encrypted_bigint(ciphertext)
    carrier=PalindromicCarrier.from_bigint(int(base["carrier_bigint_hex"],16))
    tests=[]
    for i in range(min(len(carrier.left_bits),sample_limit)):
        bits=list(carrier.left_bits); bits[i]='1' if bits[i]=='0' else '0'
        corrupted=PalindromicCarrier(2,''.join(bits),carrier.center,carrier.right_bits)
        try:
            out=decode_palindromic_carrier(corrupted); ok=int(out["ciphertext_hex"],16)==ciphertext
        except Exception: ok=False
        tests.append(ok)
    # double error in same codeword on both mirrored halves must fail closed
    l=list(carrier.left_bits); r=list(carrier.right_bits)
    for idx in (0,1): l[idx]='1' if l[idx]=='0' else '0'; r[-1-idx]='1' if r[-1-idx]=='0' else '0'
    try:
        decode_palindromic_carrier(PalindromicCarrier(2,''.join(l),carrier.center,''.join(r))); double_failed=False
    except CanonicalEncodingError: double_failed=True
    return {
        "schema":"HHS_PASS133_PALINDROMIC_ECC_STRESS_REPORT_V1","single_bit_samples":len(tests),
        "single_bit_corrected":sum(tests),"double_error_fail_closed":double_failed,
        "status":"PASS" if all(tests) and double_failed else "FAIL"
    }
