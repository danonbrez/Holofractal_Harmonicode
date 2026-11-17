"""Pass 220 integer-only orbit and prime support index; not an Ncalc evaluator."""
from collections import defaultdict
from math import isqrt

SCHEMA="HHS_PASS220_PTM_ORBIT_FACTOR_INDEX_V1"
GENERATOR="(((3*x+1)^2+(3*x+1)/2^y+41)/List(x-1==z,x==(z+w)/(2*(x^2-z*w)),x+1==w))^List(-2,1,2)"
SOURCE_GZIP_SHA256="5b9bc1bea6e0d7ebfbf5844ec39ad60c51ecba9d2a499e11d81e4f0d843c50f8"

def orbit(start):
    if type(start) is not int or start<1: raise ValueError("POSITIVE_INTEGER_REQUIRED")
    result=[start]
    while result[-1]!=1:
        n=result[-1]
        result.append(n//2 if n%2==0 else 3*n+1)
    return tuple(result)

def factors(value):
    if type(value) is not int or value<0: raise ValueError("NONNEGATIVE_INTEGER_REQUIRED")
    n=value; result={}; p=2
    while p*p<=n:
        while n%p==0:
            result[p]=result.get(p,0)+1
            n//=p
        p=3 if p==2 else p+2
    if n>1:result[n]=result.get(n,0)+1
    return result

def prime(n):
    return n>1 and factors(n)=={n:1}

def composite_index(P=9042):
    starts=(P-1,P,P+1)
    paths=tuple(orbit(x) for x in starts)
    support=defaultdict(list); direct=set()
    for root,seq in zip(starts,paths):
        for offset,n in enumerate(seq):
            p,q=n-1,n+1
            assert n*n-p*q==1
            if prime(n):direct.add(n)
            for side,value in (("p",p),("q",q)):
                for factor,exp in factors(value).items():
                    support[factor].append((root,offset,n,side,exp))
    overlap=0
    while overlap<min(map(len,paths)) and len({seq[-1-overlap] for seq in paths})==1:
        overlap+=1
    suffix=paths[0][-overlap:] if overlap else ()
    suffix_support=set()
    for n in suffix:
        suffix_support.update(factors(n-1))
        suffix_support.update(factors(n+1))
    primes={n for n in range(2,P+1) if prime(n)}
    supported=(set(support)|direct)&primes
    layers=tuple((i,n,len(paths[1])-i) for i,n in enumerate(paths[1]) if prime(n))
    return {
        "generator":GENERATOR, "starts":starts, "orbits":paths,
        "state_occurrences":sum(map(len,paths)),
        "distinct_states":len(set().union(*(set(p) for p in paths))),
        "suffix":suffix, "prime_suffixes":layers,
        "all_primes_count":len(primes), "direct_count":len(direct&primes),
        "factor_count":len(set(support)&primes),
        "combined_count":len(supported), "missing_count":len(primes-supported),
        "shared_suffix_prime_factor_count":len(suffix_support),
        "prime_factor_positions":dict(support),
        "native_ncalc_execution":"NOT_EXECUTED",
    }

def motif_index(first=1,last=31):
    paths={p:orbit(p) for p in range(first,last+1)}
    index=defaultdict(set)
    for p,seq in paths.items():
        for i in range(len(seq)):
            for j in range(i+2,len(seq)+1):
                index[seq[i:j]].add(p)
    return {
        "orbit_entries":sum(map(len,paths.values())),
        "ordered_blocks":sum(len(seq)**2 for seq in paths.values()),
        "nine_cell_positions":9*sum(len(seq)**2 for seq in paths.values()),
        "distinct_states":len(set().union(*(set(seq) for seq in paths.values()))),
        "distinct_motifs":len(index),
        "repeated_multi_orbit_motifs":sum(len(ps)>1 for ps in index.values()),
        "source_gzip_sha256":SOURCE_GZIP_SHA256,
        "generator":GENERATOR,
        "native_ncalc_execution":"NOT_EXECUTED",
    }

def receipt():
    a=composite_index();b=motif_index()
    return {
        "schema":SCHEMA,
        "P9042":{
            "orbit_lengths":tuple(map(len,a["orbits"])),
            "state_occurrences":a["state_occurrences"],
            "distinct_states":a["distinct_states"],
            "prime_layers":len(a["prime_suffixes"]),
            "shared_suffix_length":len(a["suffix"]),
            "shared_suffix_initial_state":a["suffix"][0],
            "prime_count_le_P":a["all_primes_count"],
            "direct_prime_count":a["direct_count"],
            "factor_prime_count":a["factor_count"],
            "combined_prime_support":a["combined_count"],
            "missing_primes":a["missing_count"],
            "common_suffix_prime_factors":a["shared_suffix_prime_factor_count"],
        },
        "P1_31":b,
        "native_ncalc_execution":"NOT_EXECUTED",
    }

if __name__=="__main__":
    import json
    print(json.dumps(receipt(),indent=2))
