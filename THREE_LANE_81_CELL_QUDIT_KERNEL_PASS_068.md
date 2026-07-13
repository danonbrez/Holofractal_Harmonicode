# THREE_LANE_81_CELL_QUDIT_KERNEL_PASS_068

```json
{
  "all_cells_have_three_lanes": true,
  "all_local_subgrids_closed": true,
  "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
  "cell_count": 81,
  "cells": [
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:00",
      "cell_identity_count": 1,
      "cell_root_hash72": "p2h0ISB4X70<*I>sBTI/geDUhdk*S/9xCo4+W4JGs0jBHV-)RmdgZk))8MdWll87-TXgmErm",
      "column": 0,
      "domain_id": "FORMAL_ALGEBRA",
      "energy_credit": 40,
      "global_index": 0,
      "lane_count": 3,
      "lo_shu_value": 8,
      "phase_tensor": "x",
      "proposed_energy_credit": 41,
      "row": 0,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:0",
      "transition": {
        "admitted_energy": 40,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:00",
        "current_phase": "x",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "y",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:00",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU((HtfI>UD/vTL>827zOoN!SRCg7qQc6Fu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 41,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 40,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:00",
          "constructive_proposal": true,
          "lane_root_hash72": "BFaNFvrAQ8WmUQnJ6?tvexoSHC0(ab1l*CHndcGHM7clpZPaQPjfeDt!0h)lIJwFnY41vMn5",
          "phase_state": "x",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 41,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 40,
        "transition_admitted": true,
        "transition_root_hash72": "MqI3lxg5*)SHElv>Q*QxW4YiPzNS5jpGrw)lOV8-TW>wKgeyEIYKTWW6K?ZK89xt(cxUn1TC",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:00"
          ],
          "cell_id": "cell:00",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 40,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G7+CI7VH!Yjtu5QR+XZ3rMzy5Hz?sQUb03FcOUwo>eswrvjdoBBiTvub(84-KbvF-iuRNUu9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 41,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:01",
      "cell_identity_count": 1,
      "cell_root_hash72": "rXY(esTxaTy2WYUJhAN/2!BB8MT)sPs(Qt7M4C-(?3sQHJV2SpAzQo9+<hRkh1QZ/tpLyv2T",
      "column": 1,
      "domain_id": "FORMAL_ALGEBRA",
      "energy_credit": 5,
      "global_index": 1,
      "lane_count": 3,
      "lo_shu_value": 1,
      "phase_tensor": "y",
      "proposed_energy_credit": 5,
      "row": 0,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:0",
      "transition": {
        "admitted_energy": 5,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:01",
        "current_phase": "y",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "z",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:01",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "l6Mnaw8gg4A5SI/9YFbvqzEn!Dkcb7Cry0rIAWVMvFVmLy)YJJR3I!35acXqMy76JV2!It6u",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 5,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 5,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:01",
          "constructive_proposal": true,
          "lane_root_hash72": "UdGeo6CGX<a/5-LqYvXd9TBQd2G8ctX/Mf9?x6/M1D?<DaC3UAaWTxF6Qlvk+!Hr>3q75f-o",
          "phase_state": "y",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 5,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 5,
        "transition_admitted": true,
        "transition_root_hash72": "yJfZBOeYZ+(v0/3aJLGSDw-xpJd4jl7!PBE-)N9mi7FZpLM)2k9gAnPKb)cFefNlSeE/gS2i",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:01",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 5,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "DW1i*Y1i9k1>-hVz(qM!Ip6*f-t6g*P-Eq7D0NQo3b2B6VCAazqaFlT55GsJ22LZCT>HI7Wh",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 5,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:02",
      "cell_identity_count": 1,
      "cell_root_hash72": "Y(RVMz0B!2vzF7y1D?p?Jrn90>scDMymCVDxM!+1J<AS<5fwCc4AuBlDfS6jRT/PPHYGjBrD",
      "column": 2,
      "domain_id": "FORMAL_ALGEBRA",
      "energy_credit": 30,
      "global_index": 2,
      "lane_count": 3,
      "lo_shu_value": 6,
      "phase_tensor": "z",
      "proposed_energy_credit": 29,
      "row": 0,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:0",
      "transition": {
        "admitted_energy": 30,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:02",
        "current_phase": "z",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "w",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:02",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwK0xRsaA4kpW<5srpQ>FOa?JkSjl/grroIa38-JLYraYn2xRx!w96x?fvDh)g?571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 29,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 30,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:02",
          "constructive_proposal": true,
          "lane_root_hash72": "8dH9JvGQW71/HY?8QJnjI*QCqN+zd<X5>4nrYX-iTXA3Tyk)RftNU703(h+qO+R4Dv7O(D0g",
          "phase_state": "z",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 29,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 30,
        "transition_admitted": true,
        "transition_root_hash72": "T4k>zh*WSyCq<nz6r(Kq(KuuydLf+vdLd3Sw!e<)y)BiA3eX/hHJY<ufJT7pLePzVj18sO93",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:02"
          ],
          "cell_id": "cell:02",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 30,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")YaxG2ZrjMI)Ic!1e3VSUnPu-MT?jNHmjLW5Ai0PJjO?MOY3BGJaQtH/dTjX4yLMQRT?Yvbt",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 29,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:03",
      "cell_identity_count": 1,
      "cell_root_hash72": "qTe2CH*UNU>gi5)R?evM-5cigdkOQzAnp467dAkoL9HrwOA2NjFrZKOkwhto4U5QlaqC00BO",
      "column": 3,
      "domain_id": "FORMAL_ALGEBRA",
      "energy_credit": 15,
      "global_index": 3,
      "lane_count": 3,
      "lo_shu_value": 3,
      "phase_tensor": "w",
      "proposed_energy_credit": 13,
      "row": 0,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:0",
      "transition": {
        "admitted_energy": 15,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:03",
        "current_phase": "w",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "xy",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:03",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwL?xRsaA4kpW<5srpQ>FOa?JkSjl/gsqoIa38-JLYraYn2vYs!w96x?fvDh(b5571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 13,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 15,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:03",
          "constructive_proposal": true,
          "lane_root_hash72": "YaXw6j+JAaaKs6pwfMnx/0I+rOF4*pSVv?rwQ*<BanDD<zA<t(n4c!J!kvvSCqbZ4R1wrxcD",
          "phase_state": "w",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 13,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 15,
        "transition_admitted": true,
        "transition_root_hash72": ">grT)!F4ruQp4H9I-sY)28L8A>k/9M10O<ZfZNMD7Thsq2IdWyb?n3vAskda+W3RR<<3vIio",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:03"
          ],
          "cell_id": "cell:03",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 15,
          "correction_applied": {
            "denominator": 1,
            "numerator": 2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")WhsH1ZrjMI)Ic!1e3VSUnPu-LO5jNHmjLW5Ai0PJjO?MOY3CFJaQtI*dTjX4yLMQRT?Ywat",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "proposed_energy": 13,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:04",
      "cell_identity_count": 1,
      "cell_root_hash72": "SQzN/ODP39FuclCT4yGWo90UL)3X5IcboJ1xOf+dO0xJdYn+CKqqZvPyNEgJxALc7/sioDCs",
      "column": 4,
      "domain_id": "FORMAL_ALGEBRA",
      "energy_credit": 25,
      "global_index": 4,
      "lane_count": 3,
      "lo_shu_value": 5,
      "phase_tensor": "x",
      "proposed_energy_credit": 25,
      "row": 0,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:0",
      "transition": {
        "admitted_energy": 25,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:04",
        "current_phase": "xy",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "yx",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:04",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKfyf5<7ji5wSCe(l<LJ1RXP(>tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 25,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 25,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:04",
          "constructive_proposal": true,
          "lane_root_hash72": "vlenQs+cKDusmgg8cMwqrylTWd)mBz5La/Ki/7QYEcbwvE0y3-QiRY0?WFHAF9yV+FrL3IWg",
          "phase_state": "xy",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 25,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 25,
        "transition_admitted": true,
        "transition_root_hash72": "F5PUUJxOGSpQ>PnyEENcbMIiaXGGnXOnzUdl)Pqr7Gjet0>clH2-Wrnc8?8(e>BV+7VCYCKw",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:04",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 25,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zV0dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*uiXvRgVFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 25,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:05",
      "cell_identity_count": 1,
      "cell_root_hash72": "c2VK!<pvp7!Dh*1uXi1A?+PeT(n3U>ra7(MPh-6og9-m!fjFUQUnDC*4pDKeVOC*8iKm?k4h",
      "column": 5,
      "domain_id": "FORMAL_ALGEBRA",
      "energy_credit": 35,
      "global_index": 5,
      "lane_count": 3,
      "lo_shu_value": 7,
      "phase_tensor": "y",
      "proposed_energy_credit": 37,
      "row": 0,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:0",
      "transition": {
        "admitted_energy": 35,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:05",
        "current_phase": "yx",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "zw",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:05",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bScbqpYhZ7VQWsg4/NqX>2QuGWU((MofI>UD/vTL>827yUjN!SRCg7qQc5Mo90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 37,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 35,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:05",
          "constructive_proposal": true,
          "lane_root_hash72": "OEWThbCnQKiQ/Bqw/u*U9tH<UTv*PBnxSNnUGoMbJBHj6Sll<(B9ot(b(lL0EtV>NfG>9ipT",
          "phase_state": "yx",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 37,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 35,
        "transition_admitted": true,
        "transition_root_hash72": "uhj!Fil7RcAQhL!yyRM44ifJcyU9gyzAo<Mj?4HYg-pUd-nEkBuo1gF22bPXmjC6SOQnzdvA",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:05"
          ],
          "cell_id": "cell:05",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 35,
          "correction_applied": {
            "denominator": 1,
            "numerator": -2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G6>xJ6VH!Yjtu5QR+XZ3rMzy5GG/sQUb03FcOUwo>eswrvjdtwBiTvuc/84-KbvF-iuRNZp9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "proposed_energy": 37,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:06",
      "cell_identity_count": 1,
      "cell_root_hash72": "!2>R?X40VI2Xwdg/IFT(qIMmfPPCLTc>WhXRW0Y/z*r*7l-/8?qE9ppzgC19fOkQJ?3IxdWe",
      "column": 6,
      "domain_id": "FORMAL_ALGEBRA",
      "energy_credit": 20,
      "global_index": 6,
      "lane_count": 3,
      "lo_shu_value": 4,
      "phase_tensor": "z",
      "proposed_energy_credit": 21,
      "row": 0,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:0",
      "transition": {
        "admitted_energy": 20,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:06",
        "current_phase": "zw",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "wz",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:06",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU((NnfI>UD/vTL>827xQoN!SRCg7qQc4Hu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 21,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 20,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:06",
          "constructive_proposal": true,
          "lane_root_hash72": "G*WUcw+r-JtH/3oULm6kf*QbG<6d6C-x(!c!?Mv8fj+Ud!J3Y+gsfuEG+zHwKhM8qV!OQ7N/",
          "phase_state": "zw",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 21,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 20,
        "transition_admitted": true,
        "transition_root_hash72": "xvPjV!L(XotD7V6DaUt(izpGK-V8d?Vufq1)Jad7jy1JL/w9yj?A+gLrW81XJ*Q4B*ftCFGr",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:06"
          ],
          "cell_id": "cell:06",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 20,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G5/CI7VH!Yjtu5QR+XZ3rMzy5FB?sQUb03FcOUwo>eswrvjduvBiTvub(84-KbvF-iuRN-o9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 21,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:07",
      "cell_identity_count": 1,
      "cell_root_hash72": "7k+Nw6)SoLsrQpBP9780A5+Fjq3HlfyLGaTT1eo!Kal3OOFsr+3g4gCUQ7VSiZC(ZJaMFV?R",
      "column": 7,
      "domain_id": "FORMAL_ALGEBRA",
      "energy_credit": 45,
      "global_index": 7,
      "lane_count": 3,
      "lo_shu_value": 9,
      "phase_tensor": "w",
      "proposed_energy_credit": 45,
      "row": 0,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:0",
      "transition": {
        "admitted_energy": 45,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:07",
        "current_phase": "wz",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "x",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:07",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKfBc5<7ji5yQCe(l<LJ1RXP<)tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 45,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 45,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:07",
          "constructive_proposal": true,
          "lane_root_hash72": "/IT0z/PMTnwQKYGa?V9ktdY3)>7+LhjsKw721NueyKrXNbKjZD)mGWvfWZV0269DbmkIyEH5",
          "phase_state": "wz",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 45,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 45,
        "transition_admitted": true,
        "transition_root_hash72": "FYwL<>JVG0L4ZQv-kDcPrs)?X9FMKeqe?vD6p>n5R93kWV5PMh2va+oL0uPtoyknT1Jg*+vN",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:07",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 45,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zX!dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*ulUvRiTFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 45,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:08",
      "cell_identity_count": 1,
      "cell_root_hash72": "*r!F<XRjYBfYZ8kpyUQOIZ28ftss*HIyh6KhzFvDcQYaRt-mi3j<s/rB4Pu?Hjz6Bpy*lC<G",
      "column": 8,
      "domain_id": "FORMAL_ALGEBRA",
      "energy_credit": 10,
      "global_index": 8,
      "lane_count": 3,
      "lo_shu_value": 2,
      "phase_tensor": "x",
      "proposed_energy_credit": 9,
      "row": 0,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:0",
      "transition": {
        "admitted_energy": 10,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:08",
        "current_phase": "x",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "y",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:08",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "+c6!S2t8XiE/VvfLaJRX)If8-UTHB(j0uQU>yB02Mta3Dr-FDQrik2qcxRBxDJq-d!ff*rZN",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 9,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 10,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:08",
          "constructive_proposal": true,
          "lane_root_hash72": "BFaNFvrAQ8WmUQnJ6?tvexoSHC0(ab1l*CHndcGHM7clpZPaQPjfeDt!0h)lIRoFnY41vMn5",
          "phase_state": "x",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 9,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 10,
        "transition_admitted": true,
        "transition_root_hash72": "Q?m<54b9FJgVD0Y0tK!j!o0B8)2lr*nZWDMj(XeBitcJiP<D!0vQZu)GK-EiRWr5rH-W4A<g",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:08"
          ],
          "cell_id": "cell:08",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 10,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "9zZVuHr1)RL72NV>c5SMCp*Ej2jp+yoTsuwMWbMu2?5912N1!5tIXbD4gt-flYKoTTqQ>Rv7",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 9,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:09",
      "cell_identity_count": 1,
      "cell_root_hash72": "htXf!5W0dP7eEOfK<6Jq?X4*7IFjPj9Wu88yuZ/QPWQoMPqjtocv?yiKPGMEmF>GkuDkM(tn",
      "column": 0,
      "domain_id": "SYMBOLIC_LOGIC",
      "energy_credit": 40,
      "global_index": 9,
      "lane_count": 3,
      "lo_shu_value": 8,
      "phase_tensor": "y",
      "proposed_energy_credit": 41,
      "row": 1,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:1",
      "transition": {
        "admitted_energy": 40,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:09",
        "current_phase": "y",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "z",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:09",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU((QkfI>UD/vTL>827zOoN!SRCg7qQc6Fu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 41,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 40,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:09",
          "constructive_proposal": true,
          "lane_root_hash72": "UdGeo6CGX<a/5-LqYvXd9TBQd2G8ctX/Mf9?x6/M1D?<DaC3UAaWTxF6Qlvk+6zr>3q75f-o",
          "phase_state": "y",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 41,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 40,
        "transition_admitted": true,
        "transition_root_hash72": "?V9Ic1Re71kxUuck)+d1>UDVnKQxUHM0w1/*t5epOrdcO2Ds5wzKJbR4lqy7ppPUHC9Z0i(v",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:09"
          ],
          "cell_id": "cell:09",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 40,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G7+CI7VH!Yjtu5QR+XZ3rMzy5Hz?sQUb03FcOUwo>eswrvjdxsBiTvub(84-KbvF-iuRN/l9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 41,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:10",
      "cell_identity_count": 1,
      "cell_root_hash72": ">Mc?Abfubpo*Bd<4L(Djyz*MQ8wnUb?uGTc97gWze3U?OYv2CRBy65QmkQ6x5Jqo?aLh+<j1",
      "column": 1,
      "domain_id": "SYMBOLIC_LOGIC",
      "energy_credit": 5,
      "global_index": 10,
      "lane_count": 3,
      "lo_shu_value": 1,
      "phase_tensor": "z",
      "proposed_energy_credit": 5,
      "row": 1,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:1",
      "transition": {
        "admitted_energy": 5,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:10",
        "current_phase": "z",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "w",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:10",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "l6Mnaw8gg4A5SI/9YFbvqzEn!Dkcb7Csw1rIAWVMvFVmLy)YJJR3I!35acXqMy76JV2!It6u",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 5,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 5,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:10",
          "constructive_proposal": true,
          "lane_root_hash72": "8dH9JvGQW71/HY?8QJnjI*QCqN+zd<X5>4nrYX-iTXA3Tyk)RftNU703(h+qPYT4Dv7O(D0g",
          "phase_state": "z",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 5,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 5,
        "transition_admitted": true,
        "transition_root_hash72": "qTVS7BF4WYD/J>JfAmowAB!)Vcg4vUwEhG!L39?z-RFY6jQIvq+i((?3>lpawSCh9w?dWxr3",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:10",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 5,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "DW1i*Y1i9k1>-hVz(qM!Ip6*f-t6g*P-Eq7D0NQo3b2B6VCAazqaFlT55GsK03LZCT>HI7Wh",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 5,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:11",
      "cell_identity_count": 1,
      "cell_root_hash72": "A0jsGJzS<ueKNy*4!R-kx*OsRF4?-RoSI0roLnkfb?dmRSImkkGRgFUzm>RtG)hHlUGle?i<",
      "column": 2,
      "domain_id": "SYMBOLIC_LOGIC",
      "energy_credit": 30,
      "global_index": 11,
      "lane_count": 3,
      "lo_shu_value": 6,
      "phase_tensor": "w",
      "proposed_energy_credit": 29,
      "row": 1,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:1",
      "transition": {
        "admitted_energy": 30,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:11",
        "current_phase": "w",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "xy",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:11",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwK0xRsaA4kpW<5srpQ>FOa?JkSjl/hpsoIa38-JLYraYn2xRx!w96x?fvDh)g?571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 29,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 30,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:11",
          "constructive_proposal": true,
          "lane_root_hash72": "YaXw6j+JAaaKs6pwfMnx/0I+rOF4*pSVv?rwQ*<BanDD<zA<t(n4c!J!kvvSDndZ4R1wrxcD",
          "phase_state": "w",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 29,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 30,
        "transition_admitted": true,
        "transition_root_hash72": "2erT<R/<ruQoaC8J-sY<!dJ8C*j>9N0()U+g/AYy7Tgtq2IdWzf4d3wEA0ka+Y<VF413vHkk",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:11"
          ],
          "cell_id": "cell:11",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 30,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")YaxG2ZrjMI)Ic!1e3VSUnPu-MT?jNHmjLW5Ai0PJjO?MOY4zHJaQtH/dTjX4yLMQRT?Ztct",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 29,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:12",
      "cell_identity_count": 1,
      "cell_root_hash72": "L63?4tR+e2uXUlf?CWBjY3No1B<LQW4aVP8>bpkaysmziQvenN9gGHSOAQ?tnURLm/jsH7vW",
      "column": 3,
      "domain_id": "SYMBOLIC_LOGIC",
      "energy_credit": 15,
      "global_index": 12,
      "lane_count": 3,
      "lo_shu_value": 3,
      "phase_tensor": "x",
      "proposed_energy_credit": 13,
      "row": 1,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:1",
      "transition": {
        "admitted_energy": 15,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:12",
        "current_phase": "xy",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "yx",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:12",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwL?xRsaA4kpW<5srpQ>FOa?JkSjl/hqroIa38-JLYraYn2vYs!w96x?fvDh(b5571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 13,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 15,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:12",
          "constructive_proposal": true,
          "lane_root_hash72": "vlenQs+cKDusmgg8cMwqrylTWd)mBz5La/Ki/7QYEcbwvE0y3-QiRY0?WFHAG6AV+FrL3IWg",
          "phase_state": "xy",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 13,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 15,
        "transition_admitted": true,
        "transition_root_hash72": "mBNt0ZCm>S?0-RP/NzwudvOadHMLgI+Jm>DjQwX-bK4)WOhkKi7*xP)XsWW6MK*ZzA3OUx>5",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:12"
          ],
          "cell_id": "cell:12",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 15,
          "correction_applied": {
            "denominator": 1,
            "numerator": 2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")WhsH1ZrjMI)Ic!1e3VSUnPu-LO5jNHmjLW5Ai0PJjO?MOY4AGJaQtI*dTjX4yLMQRT?Zubt",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "proposed_energy": 13,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:13",
      "cell_identity_count": 1,
      "cell_root_hash72": "Op148qc*5IS2O8cMS?-BIc5QLwbpE9e5o2BE*5fJkAL8?8pu/ly-eIslZkdiNM-ZnDw1NN71",
      "column": 4,
      "domain_id": "SYMBOLIC_LOGIC",
      "energy_credit": 25,
      "global_index": 13,
      "lane_count": 3,
      "lo_shu_value": 5,
      "phase_tensor": "y",
      "proposed_energy_credit": 25,
      "row": 1,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:1",
      "transition": {
        "admitted_energy": 25,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:13",
        "current_phase": "yx",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "zw",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:13",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKgwg5<7ji5wSCe(l<LJ1RXP(>tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 25,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 25,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:13",
          "constructive_proposal": true,
          "lane_root_hash72": "OEWThbCnQKiQ/Bqw/u*U9tH<UTv*PBnxSNnUGoMbJBHj6Sll<(B9ot(b(lL0FqX>NfG>9ipT",
          "phase_state": "yx",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 25,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 25,
        "transition_admitted": true,
        "transition_root_hash72": "dcrF>qRYwcA3z+9t!B8G6Jg*2JBdvldIvPW/0)?C+act-ylPQAm4ujXiQg*9ALWbj>Lz?6*?",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:13",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 25,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zV0dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*vgYvRgVFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 25,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:14",
      "cell_identity_count": 1,
      "cell_root_hash72": "6+ct8aQ+jGdsjnYtJ1?iUN)YUJ)8lfOr(sjwzB*J5iaDeU!Lgwpos0C2FoIX1KflC2LC!J/a",
      "column": 5,
      "domain_id": "SYMBOLIC_LOGIC",
      "energy_credit": 35,
      "global_index": 14,
      "lane_count": 3,
      "lo_shu_value": 7,
      "phase_tensor": "z",
      "proposed_energy_credit": 37,
      "row": 1,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:1",
      "transition": {
        "admitted_energy": 35,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:14",
        "current_phase": "zw",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "wz",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:14",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bScbqpYhZ7VQWsg4/NqX>2QuGWU()KpfI>UD/vTL>827yUjN!SRCg7qQc5Mo90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 37,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 35,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:14",
          "constructive_proposal": true,
          "lane_root_hash72": "G*WUcw+r-JtH/3oULm6kf*QbG<6d6C-x(!c!?Mv8fj+Ud!J3Y+gsfuEG+zHwLeO8qV!OQ7N/",
          "phase_state": "zw",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 37,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 35,
        "transition_admitted": true,
        "transition_root_hash72": "BtPjV?RU*mtD7V7K2Ut)eEnGK++!XvQwhJxgM4e7jy1JM*w9znYG+gLrYhI5J*R8y(btCFHo",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:14"
          ],
          "cell_id": "cell:14",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 35,
          "correction_applied": {
            "denominator": 1,
            "numerator": -2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G6>xJ6VH!Yjtu5QR+XZ3rMzy5GG/sQUb03FcOUwo>eswrvjerxBiTvuc/84-KbvF-iuROXq9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "proposed_energy": 37,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:15",
      "cell_identity_count": 1,
      "cell_root_hash72": "EnA(NCMMu*nzfeZyCJSxIC8IfPA8iK67P>oiSEktUosjmdLA?>srkDCQgV8w7lLPoRIkcRgO",
      "column": 6,
      "domain_id": "SYMBOLIC_LOGIC",
      "energy_credit": 20,
      "global_index": 15,
      "lane_count": 3,
      "lo_shu_value": 4,
      "phase_tensor": "w",
      "proposed_energy_credit": 21,
      "row": 1,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:1",
      "transition": {
        "admitted_energy": 20,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:15",
        "current_phase": "wz",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "x",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:15",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU()LofI>UD/vTL>827xQoN!SRCg7qQc4Hu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 21,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 20,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:15",
          "constructive_proposal": true,
          "lane_root_hash72": "/IT0z/PMTnwQKYGa?V9ktdY3)>7+LhjsKw721NueyKrXNbKjZD)mGWvfWZV033bDbmkIyEH5",
          "phase_state": "wz",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 21,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 20,
        "transition_admitted": true,
        "transition_root_hash72": "4I>J-gYJQt61RlVhPQ>m?TJq>C>j+d4D*HNxWung9*L74<7N/N33mgaoK0M<(4yn//7MyVuk",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:15"
          ],
          "cell_id": "cell:15",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 20,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G5/CI7VH!Yjtu5QR+XZ3rMzy5FB?sQUb03FcOUwo>eswrvjeswBiTvub(84-KbvF-iuROYp9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 21,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:16",
      "cell_identity_count": 1,
      "cell_root_hash72": "A2F*)>MHlL2*9GyAN9dUieW7z!cFMS4C-4CQwKJfryZb<8D!3gYMY7+7FQxKuxf(Fmx6LRT*",
      "column": 7,
      "domain_id": "SYMBOLIC_LOGIC",
      "energy_credit": 45,
      "global_index": 16,
      "lane_count": 3,
      "lo_shu_value": 9,
      "phase_tensor": "x",
      "proposed_energy_credit": 45,
      "row": 1,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:1",
      "transition": {
        "admitted_energy": 45,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:16",
        "current_phase": "x",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "y",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:16",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKgzd5<7ji5yQCe(l<LJ1RXP<)tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 45,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 45,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:16",
          "constructive_proposal": true,
          "lane_root_hash72": "BFaNFvrAQ8WmUQnJ6?tvexoSHC0(ab1l*CHndcGHM7clpZPaQPjfeDt!0h)lJOqFnY41vMn5",
          "phase_state": "x",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 45,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 45,
        "transition_admitted": true,
        "transition_root_hash72": "*y9mLJahjOxC*zuA+KTe)4Cro1Qt?k7RtYCnGIzCronEtUk<RxsZ4mIdZC?u3jyrnKMw9zCs",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:16",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 45,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zX!dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*vjVvRiTFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 45,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:17",
      "cell_identity_count": 1,
      "cell_root_hash72": "/94Yo-6PxQX(>rmoANRXTnq-p76b*D<3--QI1h!T1yjXANcIW<pJL8rxfWIZXtd<B*QBQH9k",
      "column": 8,
      "domain_id": "SYMBOLIC_LOGIC",
      "energy_credit": 10,
      "global_index": 17,
      "lane_count": 3,
      "lo_shu_value": 2,
      "phase_tensor": "y",
      "proposed_energy_credit": 9,
      "row": 1,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:1",
      "transition": {
        "admitted_energy": 10,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:17",
        "current_phase": "y",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "z",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:17",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "+c6!S2t8XiE/VvfLaJRX)If8-UTHB(j1sRU>yB02Mta3Dr-FDQrik2qcxRBxDJq-d!ff*rZN",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 9,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 10,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:17",
          "constructive_proposal": true,
          "lane_root_hash72": "UdGeo6CGX<a/5-LqYvXd9TBQd2G8ctX/Mf9?x6/M1D?<DaC3UAaWTxF6Qlvk*3Br>3q75f-o",
          "phase_state": "y",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 9,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 10,
        "transition_admitted": true,
        "transition_root_hash72": "3vdbW4piUPSLT9FnIJn233mvUwXR5qKj*6C?J7k0d!spmBlxzY6QPUYwuhdP!2Jw4>C+QHGV",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:17"
          ],
          "cell_id": "cell:17",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 10,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "9zZVuHr1)RL72NV>c5SMCp*Ej2jp+yoTsuwMWbMu2?5912N2<6tIXbD4gt-flYKoTTqQ!Pw7",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 9,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:18",
      "cell_identity_count": 1,
      "cell_root_hash72": "gtc9(cN6szCzXi58AZbp!XXsIUIbnpacPll1o8ql6qh<HzcBFxn+3juyS4Zts+eS/JS1/c(r",
      "column": 0,
      "domain_id": "SEMANTIC_TRANSLATION",
      "energy_credit": 40,
      "global_index": 18,
      "lane_count": 3,
      "lo_shu_value": 8,
      "phase_tensor": "z",
      "proposed_energy_credit": 41,
      "row": 2,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:2",
      "transition": {
        "admitted_energy": 40,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:18",
        "current_phase": "z",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "w",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:18",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU()OlfI>UD/vTL>827zOoN!SRCg7qQc6Fu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 41,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 40,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:18",
          "constructive_proposal": true,
          "lane_root_hash72": "8dH9JvGQW71/HY?8QJnjI*QCqN+zd<X5>4nrYX-iTXA3Tyk)RftNU703(h+qP<L4Dv7O(D0g",
          "phase_state": "z",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 41,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 40,
        "transition_admitted": true,
        "transition_root_hash72": ")cq7qLvD*/u3N0?LbZ6QruHruuyczER8(xv>shNOk/iFyc?jh49KLZq50TEZrTm40oz2FWp6",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:18"
          ],
          "cell_id": "cell:18",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 40,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G7+CI7VH!Yjtu5QR+XZ3rMzy5Hz?sQUb03FcOUwo>eswrvjevtBiTvub(84-KbvF-iuRO+m9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 41,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:19",
      "cell_identity_count": 1,
      "cell_root_hash72": "/-EIp)8t09mgRmADca+Dx8lbCd*KYeEaAq(x)ZAu6sF4/YbNK<+x(S(CXhzFx2dBwtJ4zX<b",
      "column": 1,
      "domain_id": "SEMANTIC_TRANSLATION",
      "energy_credit": 5,
      "global_index": 19,
      "lane_count": 3,
      "lo_shu_value": 1,
      "phase_tensor": "w",
      "proposed_energy_credit": 5,
      "row": 2,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:2",
      "transition": {
        "admitted_energy": 5,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:19",
        "current_phase": "w",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "xy",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:19",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "l6Mnaw8gg4A5SI/9YFbvqzEn!Dkcb7CsF*rIAWVMvFVmLy)YJJR3I!35acXqMy76JV2!It6u",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 5,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 5,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:19",
          "constructive_proposal": true,
          "lane_root_hash72": "YaXw6j+JAaaKs6pwfMnx/0I+rOF4*pSVv?rwQ*<BanDD<zA<t(n4c!J!kvvSDv5Z4R1wrxcD",
          "phase_state": "w",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 5,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 5,
        "transition_admitted": true,
        "transition_root_hash72": "G/OJz6XHDc)i8pVCqqXgG>1dwR+tdZOaYlLUghL?CNN*0qrgxP0S!jXaQd>1GGX5+*uS6Eqq",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:19",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 5,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "DW1i*Y1i9k1>-hVz(qM!Ip6*f-t6g*P-Eq7D0NQo3b2B6VCAazqaFlT55GsK9(LZCT>HI7Wh",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 5,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:20",
      "cell_identity_count": 1,
      "cell_root_hash72": "pD>/SWAY5Y+kmgcIgjN7kze4V2/YifnELgugZwtV4SBOukkcbPZ<ai7g2)X(X329svnjSZ/P",
      "column": 2,
      "domain_id": "SEMANTIC_TRANSLATION",
      "energy_credit": 30,
      "global_index": 20,
      "lane_count": 3,
      "lo_shu_value": 6,
      "phase_tensor": "x",
      "proposed_energy_credit": 29,
      "row": 2,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:2",
      "transition": {
        "admitted_energy": 30,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:20",
        "current_phase": "xy",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "yx",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:20",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwK0xRsaA4kpW<5srpQ>FOa?JkSjl/intoIa38-JLYraYn2xRx!w96x?fvDh)g?571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 29,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 30,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:20",
          "constructive_proposal": true,
          "lane_root_hash72": "vlenQs+cKDusmgg8cMwqrylTWd)mBz5La/Ki/7QYEcbwvE0y3-QiRY0?WFHAH3CV+FrL3IWg",
          "phase_state": "xy",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 29,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 30,
        "transition_admitted": true,
        "transition_root_hash72": "iGLt0ZE9aQ?0-QVYMAwuerT8dHQZ)N-GqZU7SzQ!6K4)VPhkKi8<CF)XvT>/OK*+rtbTUx<7",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:20"
          ],
          "cell_id": "cell:20",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 30,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")YaxG2ZrjMI)Ic!1e3VSUnPu-MT?jNHmjLW5Ai0PJjO?MOY5xIJaQtH/dTjX4yLMQRT?-rdt",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 29,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:21",
      "cell_identity_count": 1,
      "cell_root_hash72": "F70YKKloZzq4>SO068oGMAvRvaV1lY(1>r(x*o/Pf6y6K)W4wB64uUXg5sKg5>uO+KA?oMRg",
      "column": 3,
      "domain_id": "SEMANTIC_TRANSLATION",
      "energy_credit": 15,
      "global_index": 21,
      "lane_count": 3,
      "lo_shu_value": 3,
      "phase_tensor": "y",
      "proposed_energy_credit": 13,
      "row": 2,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:2",
      "transition": {
        "admitted_energy": 15,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:21",
        "current_phase": "yx",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "zw",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:21",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwL?xRsaA4kpW<5srpQ>FOa?JkSjl/iosoIa38-JLYraYn2vYs!w96x?fvDh(b5571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 13,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 15,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:21",
          "constructive_proposal": true,
          "lane_root_hash72": "OEWThbCnQKiQ/Bqw/u*U9tH<UTv*PBnxSNnUGoMbJBHj6Sll<(B9ot(b(lL0GnZ>NfG>9ipT",
          "phase_state": "yx",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 13,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 15,
        "transition_admitted": true,
        "transition_root_hash72": "cdYEE76NlsXaI1ZT7KT)tbNDa28/WjAB8+bsd<6X6jM02oq6cboo(5wkk61MFa!xQki0ySnx",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:21"
          ],
          "cell_id": "cell:21",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 15,
          "correction_applied": {
            "denominator": 1,
            "numerator": 2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")WhsH1ZrjMI)Ic!1e3VSUnPu-LO5jNHmjLW5Ai0PJjO?MOY5yHJaQtI*dTjX4yLMQRT?-sct",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "proposed_energy": 13,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:22",
      "cell_identity_count": 1,
      "cell_root_hash72": "FE-ngtLNOEKUi<VwQyLEPCE46cBD>XK(ge3ERc>Ug/f5SLeKrL>VLeUCpY(xqVxVo!f9jgOS",
      "column": 4,
      "domain_id": "SEMANTIC_TRANSLATION",
      "energy_credit": 25,
      "global_index": 22,
      "lane_count": 3,
      "lo_shu_value": 5,
      "phase_tensor": "z",
      "proposed_energy_credit": 25,
      "row": 2,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:2",
      "transition": {
        "admitted_energy": 25,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:22",
        "current_phase": "zw",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "wz",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:22",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKhuh5<7ji5wSCe(l<LJ1RXP(>tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 25,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 25,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:22",
          "constructive_proposal": true,
          "lane_root_hash72": "G*WUcw+r-JtH/3oULm6kf*QbG<6d6C-x(!c!?Mv8fj+Ud!J3Y+gsfuEG+zHwMbQ8qV!OQ7N/",
          "phase_state": "zw",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 25,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 25,
        "transition_admitted": true,
        "transition_root_hash72": "I*AN/cH!Fo46hOpL7yG?bBYWkFvZfjZK1!ZBMUyH(RuclNhNU-89pAa+)iIp)RZDvVSLvr8Q",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:22",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 25,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zV0dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*weZvRgVFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 25,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:23",
      "cell_identity_count": 1,
      "cell_root_hash72": "jYuZnUd4ULNy/)uA71>6O(GQUrVwLVBnUOy+>vwEm1SUxqz!j5sisWWLfH-TPam+fH2)60xB",
      "column": 5,
      "domain_id": "SEMANTIC_TRANSLATION",
      "energy_credit": 35,
      "global_index": 23,
      "lane_count": 3,
      "lo_shu_value": 7,
      "phase_tensor": "w",
      "proposed_energy_credit": 37,
      "row": 2,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:2",
      "transition": {
        "admitted_energy": 35,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:23",
        "current_phase": "wz",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "x",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:23",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bScbqpYhZ7VQWsg4/NqX>2QuGWU(<IqfI>UD/vTL>827yUjN!SRCg7qQc5Mo90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 37,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 35,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:23",
          "constructive_proposal": true,
          "lane_root_hash72": "/IT0z/PMTnwQKYGa?V9ktdY3)>7+LhjsKw721NueyKrXNbKjZD)mGWvfWZV040dDbmkIyEH5",
          "phase_state": "wz",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 37,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 35,
        "transition_admitted": true,
        "transition_root_hash72": "2I>J+mOOOt61Rm*9PQg04RJq!H+e?86Fb3!AQvng9*L83<7O>C93mgapQQZ<(5Ck)Z7MyWro",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:23"
          ],
          "cell_id": "cell:23",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 35,
          "correction_applied": {
            "denominator": 1,
            "numerator": -2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G6>xJ6VH!Yjtu5QR+XZ3rMzy5GG/sQUb03FcOUwo>eswrvjfpyBiTvuc/84-KbvF-iuRPVr9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "proposed_energy": 37,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:24",
      "cell_identity_count": 1,
      "cell_root_hash72": "ErUt(y9>7YpG)Ilq0yW>1y1HMUgF0BtmRC7NLsHMaQXrUVj8>8s3)IzMGwD!/W4tN8m0*QF3",
      "column": 6,
      "domain_id": "SEMANTIC_TRANSLATION",
      "energy_credit": 20,
      "global_index": 24,
      "lane_count": 3,
      "lo_shu_value": 4,
      "phase_tensor": "x",
      "proposed_energy_credit": 21,
      "row": 2,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:2",
      "transition": {
        "admitted_energy": 20,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:24",
        "current_phase": "x",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "y",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:24",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU(<JpfI>UD/vTL>827xQoN!SRCg7qQc4Hu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 21,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 20,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:24",
          "constructive_proposal": true,
          "lane_root_hash72": "BFaNFvrAQ8WmUQnJ6?tvexoSHC0(ab1l*CHndcGHM7clpZPaQPjfeDt!0h)lKLsFnY41vMn5",
          "phase_state": "x",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 21,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 20,
        "transition_admitted": true,
        "transition_root_hash72": "MqI3ndy5*)SHElv>Qcyr-4WkTBF-3bxCru3fOV8-TW>wKgcCCIYKTU6*E1ZIa9vv(cxUp1NG",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:24"
          ],
          "cell_id": "cell:24",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 20,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G5/CI7VH!Yjtu5QR+XZ3rMzy5FB?sQUb03FcOUwo>eswrvjfqxBiTvub(84-KbvF-iuRPWq9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 21,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:25",
      "cell_identity_count": 1,
      "cell_root_hash72": "nRMKe4WbCWqM1Ugbzyj/hdS*K0UGB-z6jX6euT>IVh24LkmG6C?O224?GBdbUo/5yUau-l1-",
      "column": 7,
      "domain_id": "SEMANTIC_TRANSLATION",
      "energy_credit": 45,
      "global_index": 25,
      "lane_count": 3,
      "lo_shu_value": 9,
      "phase_tensor": "y",
      "proposed_energy_credit": 45,
      "row": 2,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:2",
      "transition": {
        "admitted_energy": 45,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:25",
        "current_phase": "y",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "z",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:25",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKhxe5<7ji5yQCe(l<LJ1RXP<)tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 45,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 45,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:25",
          "constructive_proposal": true,
          "lane_root_hash72": "UdGeo6CGX<a/5-LqYvXd9TBQd2G8ctX/Mf9?x6/M1D?<DaC3UAaWTxF6Qlvk/0Dr>3q75f-o",
          "phase_state": "y",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 45,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 45,
        "transition_admitted": true,
        "transition_root_hash72": "3Knsdzqq01NyjkwgGdrSOCfZLwU>Z0W1znx*WoCqOiZs5TamLmcgNTZt7/MUPoeu>f?+K4kt",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:25",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 45,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zX!dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*whWvRiTFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 45,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:26",
      "cell_identity_count": 1,
      "cell_root_hash72": "c3XF)qcHqKDPqe<IC+80lMCp4mXxNjdRaj)b+F*aq(Rntnm3?hUa(vpVkXCCd*L3IxQabPy!",
      "column": 8,
      "domain_id": "SEMANTIC_TRANSLATION",
      "energy_credit": 10,
      "global_index": 26,
      "lane_count": 3,
      "lo_shu_value": 2,
      "phase_tensor": "z",
      "proposed_energy_credit": 9,
      "row": 2,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:2",
      "transition": {
        "admitted_energy": 10,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:26",
        "current_phase": "z",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "w",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:26",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "+c6!S2t8XiE/VvfLaJRX)If8-UTHB(j2qSU>yB02Mta3Dr-FDQrik2qcxRBxDJq-d!ff*rZN",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 9,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 10,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:26",
          "constructive_proposal": true,
          "lane_root_hash72": "8dH9JvGQW71/HY?8QJnjI*QCqN+zd<X5>4nrYX-iTXA3Tyk)RftNU703(h+qQ/N4Dv7O(D0g",
          "phase_state": "z",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 9,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 10,
        "transition_admitted": true,
        "transition_root_hash72": "?X9(2L4HFH*hMPsOYGkLBMUF/kAxUnPrrz73IjTpTAxS6LRoLwQQRzuA8Kjx0wgQxT*4n?>K",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:26"
          ],
          "cell_id": "cell:26",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 10,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "9zZVuHr1)RL72NV>c5SMCp*Ej2jp+yoTsuwMWbMu2?5912N3(7tIXbD4gt-flYKoTTqQ?Nx7",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 9,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:27",
      "cell_identity_count": 1,
      "cell_root_hash72": "ZA2MoY6VHnw6/*/7vhtQBnQprq<SRkJWA9QiF8nUFk1b3oMra?7z7rv-8?psbwl3dcxlh5oo",
      "column": 0,
      "domain_id": "RUNTIME_EXECUTION",
      "energy_credit": 40,
      "global_index": 27,
      "lane_count": 3,
      "lo_shu_value": 8,
      "phase_tensor": "w",
      "proposed_energy_credit": 41,
      "row": 3,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:3",
      "transition": {
        "admitted_energy": 40,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:27",
        "current_phase": "w",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "xy",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:27",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU(<MmfI>UD/vTL>827zOoN!SRCg7qQc6Fu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 41,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 40,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:27",
          "constructive_proposal": true,
          "lane_root_hash72": "YaXw6j+JAaaKs6pwfMnx/0I+rOF4*pSVv?rwQ*<BanDD<zA<t(n4c!J!kvvSEs7Z4R1wrxcD",
          "phase_state": "w",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 41,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 40,
        "transition_admitted": true,
        "transition_root_hash72": "L<10tJAo**WW!<PVJDj!G-+0K5pDeTk</DK4>f*)sXjbD8Xd19+YIx?qsGwcFD-V9bmyA8YP",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:27"
          ],
          "cell_id": "cell:27",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 40,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G7+CI7VH!Yjtu5QR+XZ3rMzy5Hz?sQUb03FcOUwo>eswrvjftuBiTvub(84-KbvF-iuRPZn9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 41,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:28",
      "cell_identity_count": 1,
      "cell_root_hash72": "JSMqgmwHBrWrod)/Otbx3Gg*KZgmSKoEN!)m/IPzsErTzl*>15OHEyiLo3jsCSk*O6zqIwTp",
      "column": 1,
      "domain_id": "RUNTIME_EXECUTION",
      "energy_credit": 5,
      "global_index": 28,
      "lane_count": 3,
      "lo_shu_value": 1,
      "phase_tensor": "x",
      "proposed_energy_credit": 5,
      "row": 3,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:3",
      "transition": {
        "admitted_energy": 5,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:28",
        "current_phase": "xy",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "yx",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:28",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "l6Mnaw8gg4A5SI/9YFbvqzEn!Dkcb7CtD/rIAWVMvFVmLy)YJJR3I!35acXqMy76JV2!It6u",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 5,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 5,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:28",
          "constructive_proposal": true,
          "lane_root_hash72": "vlenQs+cKDusmgg8cMwqrylTWd)mBz5La/Ki/7QYEcbwvE0y3-QiRY0?WFHAHbuV+FrL3IWg",
          "phase_state": "xy",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 5,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 5,
        "transition_admitted": true,
        "transition_root_hash72": ">1MDxSMzjbH<bnbOm3(F<ABXEIh-?qz6v7r1zTO6R*Q)s1GjN-iVrRmbVv7b2PeOAmSBV<Kg",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:28",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 5,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "DW1i*Y1i9k1>-hVz(qM!Ip6*f-t6g*P-Eq7D0NQo3b2B6VCAazqaFlT55GsL7)LZCT>HI7Wh",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 5,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:29",
      "cell_identity_count": 1,
      "cell_root_hash72": "4!CjF*yh8Sv1rJwAi-w)Sc5?y<CI<vUV)UEEzGB-lnkI7*QS*-xuO?oGBYM7mMQfR?rr5OsQ",
      "column": 2,
      "domain_id": "RUNTIME_EXECUTION",
      "energy_credit": 30,
      "global_index": 29,
      "lane_count": 3,
      "lo_shu_value": 6,
      "phase_tensor": "y",
      "proposed_energy_credit": 29,
      "row": 3,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:3",
      "transition": {
        "admitted_energy": 30,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:29",
        "current_phase": "yx",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "zw",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:29",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwK0xRsaA4kpW<5srpQ>FOa?JkSjl/iwkoIa38-JLYraYn2xRx!w96x?fvDh)g?571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 29,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 30,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:29",
          "constructive_proposal": true,
          "lane_root_hash72": "OEWThbCnQKiQ/Bqw/u*U9tH<UTv*PBnxSNnUGoMbJBHj6Sll<(B9ot(b(lL0GvR>NfG>9ipT",
          "phase_state": "yx",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 29,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 30,
        "transition_admitted": true,
        "transition_root_hash72": "k><EE774HOXaI0)O6LT)tjxLa2a2>mbJ2Tsgf!aV1jM01pq6cbps?)wkn3bKxa!zIdq5ySmy",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:29"
          ],
          "cell_id": "cell:29",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 30,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")YaxG2ZrjMI)Ic!1e3VSUnPu-MT?jNHmjLW5Ai0PJjO?MOY5GzJaQtH/dTjX4yLMQRT?-A4t",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 29,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:30",
      "cell_identity_count": 1,
      "cell_root_hash72": "MDEd?FlXhTCaRzwwLD9BSiSL62n(k6umOZZZQjEdl)WWKYavuIG57kuh5Xd-3hWJ)TTc4UKM",
      "column": 3,
      "domain_id": "RUNTIME_EXECUTION",
      "energy_credit": 15,
      "global_index": 30,
      "lane_count": 3,
      "lo_shu_value": 3,
      "phase_tensor": "z",
      "proposed_energy_credit": 13,
      "row": 3,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:3",
      "transition": {
        "admitted_energy": 15,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:30",
        "current_phase": "zw",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "wz",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:30",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwL?xRsaA4kpW<5srpQ>FOa?JkSjl/jmtoIa38-JLYraYn2vYs!w96x?fvDh(b5571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 13,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 15,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:30",
          "constructive_proposal": true,
          "lane_root_hash72": "G*WUcw+r-JtH/3oULm6kf*QbG<6d6C-x(!c!?Mv8fj+Ud!J3Y+gsfuEG+zHwN8S8qV!OQ7N/",
          "phase_state": "zw",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 13,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 15,
        "transition_admitted": true,
        "transition_root_hash72": "xX00ZnY54z!3v+?*jeWMkl?L7AD*Q(tT4UYdaJ6upmkM+UB7Rt9Sc)wqJ*7FXxHMS0yvEVPJ",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:30"
          ],
          "cell_id": "cell:30",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 15,
          "correction_applied": {
            "denominator": 1,
            "numerator": 2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")WhsH1ZrjMI)Ic!1e3VSUnPu-LO5jNHmjLW5Ai0PJjO?MOY6wIJaQtI*dTjX4yLMQRT?+qdt",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "proposed_energy": 13,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:31",
      "cell_identity_count": 1,
      "cell_root_hash72": "EDgjXJtoVABcnkQmUai6D/tUVvW/vZ)dgqptzjcyOF-)*9rDJ/SX+T9ytysFm)439-mUDxi(",
      "column": 4,
      "domain_id": "RUNTIME_EXECUTION",
      "energy_credit": 25,
      "global_index": 31,
      "lane_count": 3,
      "lo_shu_value": 5,
      "phase_tensor": "w",
      "proposed_energy_credit": 25,
      "row": 3,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:3",
      "transition": {
        "admitted_energy": 25,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:31",
        "current_phase": "wz",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "x",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:31",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKisi5<7ji5wSCe(l<LJ1RXP(>tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 25,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 25,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:31",
          "constructive_proposal": true,
          "lane_root_hash72": "/IT0z/PMTnwQKYGa?V9ktdY3)>7+LhjsKw721NueyKrXNbKjZD)mGWvfWZV05>fDbmkIyEH5",
          "phase_state": "wz",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 25,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 25,
        "transition_admitted": true,
        "transition_root_hash72": "F+kgA>HZE0L7z9p-kDaPrw<-/7NuWcH??b8Vp>n5Rc(qWV3RMh2va+oL!uRtoykqYC0g*+tP",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:31",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 25,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zV0dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*xc-vRgVFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 25,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:32",
      "cell_identity_count": 1,
      "cell_root_hash72": "1)RN7n-?UHrDYHU4/RsBTS-iPyw6SOvdnJGPvCI)7QH5!ZgtgT8B1imxgVe8JHHEGs>DB6hG",
      "column": 5,
      "domain_id": "RUNTIME_EXECUTION",
      "energy_credit": 35,
      "global_index": 32,
      "lane_count": 3,
      "lo_shu_value": 7,
      "phase_tensor": "x",
      "proposed_energy_credit": 37,
      "row": 3,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:3",
      "transition": {
        "admitted_energy": 35,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:32",
        "current_phase": "x",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "y",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:32",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bScbqpYhZ7VQWsg4/NqX>2QuGWU(>GrfI>UD/vTL>827yUjN!SRCg7qQc5Mo90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 37,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 35,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:32",
          "constructive_proposal": true,
          "lane_root_hash72": "BFaNFvrAQ8WmUQnJ6?tvexoSHC0(ab1l*CHndcGHM7clpZPaQPjfeDt!0h)lLIuFnY41vMn5",
          "phase_state": "x",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 37,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 35,
        "transition_admitted": true,
        "transition_root_hash72": "MqI5ocw5*)SILdv>QetwY4XoQuNW2fQ!Lv92TV8-TX<wKgdGrOYKTVbEX5UJe4xx-cxUq!RE",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:32"
          ],
          "cell_id": "cell:32",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 35,
          "correction_applied": {
            "denominator": 1,
            "numerator": -2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G6>xJ6VH!Yjtu5QR+XZ3rMzy5GG/sQUb03FcOUwo>eswrvjgnzBiTvuc/84-KbvF-iuRQTs9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "proposed_energy": 37,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:33",
      "cell_identity_count": 1,
      "cell_root_hash72": "ey)x?OHt(y!zed8ag9LRa8Igi6>8?ATSj3KT0XG<dn/!IYSdt+wW+cmLplEtlw>gkxkz+Hwm",
      "column": 6,
      "domain_id": "RUNTIME_EXECUTION",
      "energy_credit": 20,
      "global_index": 33,
      "lane_count": 3,
      "lo_shu_value": 4,
      "phase_tensor": "y",
      "proposed_energy_credit": 21,
      "row": 3,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:3",
      "transition": {
        "admitted_energy": 20,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:33",
        "current_phase": "y",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "z",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:33",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU(>HqfI>UD/vTL>827xQoN!SRCg7qQc4Hu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 21,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 20,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:33",
          "constructive_proposal": true,
          "lane_root_hash72": "UdGeo6CGX<a/5-LqYvXd9TBQd2G8ctX/Mf9?x6/M1D?<DaC3UAaWTxF6Qlvk(>Fr>3q75f-o",
          "phase_state": "y",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 21,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 20,
        "transition_admitted": true,
        "transition_root_hash72": "?V9J2gLe71kxUuck)dSg+UBXt0tlRJU<w0-<t5epOrdcO2Bw3wzKJ92Ppsy5rpNWHC9Z>t6b",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:33"
          ],
          "cell_id": "cell:33",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 20,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G5/CI7VH!Yjtu5QR+XZ3rMzy5FB?sQUb03FcOUwo>eswrvjgoyBiTvub(84-KbvF-iuRQUr9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 21,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:34",
      "cell_identity_count": 1,
      "cell_root_hash72": "3rOOopeT/okuRRBhMNu7(3qP+YbT-ADO16*kFSVQQa?altajUICZrXmX<7NhN0yVmDx(Eh>b",
      "column": 7,
      "domain_id": "RUNTIME_EXECUTION",
      "energy_credit": 45,
      "global_index": 34,
      "lane_count": 3,
      "lo_shu_value": 9,
      "phase_tensor": "z",
      "proposed_energy_credit": 45,
      "row": 3,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:3",
      "transition": {
        "admitted_energy": 45,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:34",
        "current_phase": "z",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "w",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:34",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKivf5<7ji5yQCe(l<LJ1RXP<)tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 45,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 45,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:34",
          "constructive_proposal": true,
          "lane_root_hash72": "8dH9JvGQW71/HY?8QJnjI*QCqN+zd<X5>4nrYX-iTXA3Tyk)RftNU703(h+qR-P4Dv7O(D0g",
          "phase_state": "z",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 45,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 45,
        "transition_admitted": true,
        "transition_root_hash72": "P27kn5j<Xs(si)+-KTwJpk/WQFhru4Vd!M3u+Rpy8920MWc1ip-JTB+XOd5G5BR+n4)i+CB1",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:34",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 45,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zX!dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*xfXvRiTFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 45,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:35",
      "cell_identity_count": 1,
      "cell_root_hash72": "pX5g/)hczO*/LT2q4Ih-X27tWTKA?lKf*l?Vwuqra1(p/w7RSJkpoZmwBpr?5!vcoCf*NZc?",
      "column": 8,
      "domain_id": "RUNTIME_EXECUTION",
      "energy_credit": 10,
      "global_index": 35,
      "lane_count": 3,
      "lo_shu_value": 2,
      "phase_tensor": "w",
      "proposed_energy_credit": 9,
      "row": 3,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:3",
      "transition": {
        "admitted_energy": 10,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:35",
        "current_phase": "w",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "xy",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:35",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "+c6!S2t8XiE/VvfLaJRX)If8-UTHB(j3oTU>yB02Mta3Dr-FDQrik2qcxRBxDJq-d!ff*rZN",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 9,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 10,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:35",
          "constructive_proposal": true,
          "lane_root_hash72": "YaXw6j+JAaaKs6pwfMnx/0I+rOF4*pSVv?rwQ*<BanDD<zA<t(n4c!J!kvvSFp9Z4R1wrxcD",
          "phase_state": "w",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 9,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 10,
        "transition_admitted": true,
        "transition_root_hash72": "f0MUfnx!<FAkc)ueMgRyv48!1GFbF23(c1JT2v(13m-qQQm)6DjvODKrXTk+dcDPVIR+C-bd",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:35"
          ],
          "cell_id": "cell:35",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 10,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "9zZVuHr1)RL72NV>c5SMCp*Ej2jp+yoTsuwMWbMu2?5912N4*8tIXbD4gt-flYKoTTqQ0Ly7",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 9,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:36",
      "cell_identity_count": 1,
      "cell_root_hash72": "x2XWp8Txe/7kpm(mqB*x>4HB?OvbY3i*11DLyhN<2wow-jy8(78VSANT<XNjdl81k8ja?jN6",
      "column": 0,
      "domain_id": "PROVENANCE_AUDIT",
      "energy_credit": 40,
      "global_index": 36,
      "lane_count": 3,
      "lo_shu_value": 8,
      "phase_tensor": "x",
      "proposed_energy_credit": 41,
      "row": 4,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:4",
      "transition": {
        "admitted_energy": 40,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:36",
        "current_phase": "xy",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "yx",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:36",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU(>KnfI>UD/vTL>827zOoN!SRCg7qQc6Fu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 41,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 40,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:36",
          "constructive_proposal": true,
          "lane_root_hash72": "vlenQs+cKDusmgg8cMwqrylTWd)mBz5La/Ki/7QYEcbwvE0y3-QiRY0?WFHAI8wV+FrL3IWg",
          "phase_state": "xy",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 41,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 40,
        "transition_admitted": true,
        "transition_root_hash72": "Jk8unQJ17pq!>B7>vubb>nWMR5ZgB/EOw>bDzUL/HikEDPF!vbbVLP8aUILOWd)T3vyJeX7B",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:36"
          ],
          "cell_id": "cell:36",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 40,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G7+CI7VH!Yjtu5QR+XZ3rMzy5Hz?sQUb03FcOUwo>eswrvjgrvBiTvub(84-KbvF-iuRQXo9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 41,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:37",
      "cell_identity_count": 1,
      "cell_root_hash72": "95L<<mC1u++lmRW-8iZ>lD*ybs2kMK07IFvv-pmiTYEK8Zb-vuOgQZPfS!muddM54gqyDSDo",
      "column": 1,
      "domain_id": "PROVENANCE_AUDIT",
      "energy_credit": 5,
      "global_index": 37,
      "lane_count": 3,
      "lo_shu_value": 1,
      "phase_tensor": "y",
      "proposed_energy_credit": 5,
      "row": 4,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:4",
      "transition": {
        "admitted_energy": 5,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:37",
        "current_phase": "yx",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "zw",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:37",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "l6Mnaw8gg4A5SI/9YFbvqzEn!Dkcb7CuB(rIAWVMvFVmLy)YJJR3I!35acXqMy76JV2!It6u",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 5,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 5,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:37",
          "constructive_proposal": true,
          "lane_root_hash72": "OEWThbCnQKiQ/Bqw/u*U9tH<UTv*PBnxSNnUGoMbJBHj6Sll<(B9ot(b(lL0HsT>NfG>9ipT",
          "phase_state": "yx",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 5,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 5,
        "transition_admitted": true,
        "transition_root_hash72": "VbuXHI6KGMWQ4Mf9Q!+dGsnRcSNolmuP3cHKKEg?!odl(wAB*yalxpD)0RVws7B7xxmTpB2I",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:37",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 5,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "DW1i*Y1i9k1>-hVz(qM!Ip6*f-t6g*P-Eq7D0NQo3b2B6VCAazqaFlT55GsM5<LZCT>HI7Wh",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 5,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:38",
      "cell_identity_count": 1,
      "cell_root_hash72": "fbRDNcnyuC8nM>ZqKEI-Q/xg*9tdrXBmn5d8kxL1XxADG1VZ!0aM41)AGUHSTfZxoBGOJ(XD",
      "column": 2,
      "domain_id": "PROVENANCE_AUDIT",
      "energy_credit": 30,
      "global_index": 38,
      "lane_count": 3,
      "lo_shu_value": 6,
      "phase_tensor": "z",
      "proposed_energy_credit": 29,
      "row": 4,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:4",
      "transition": {
        "admitted_energy": 30,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:38",
        "current_phase": "zw",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "wz",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:38",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwK0xRsaA4kpW<5srpQ>FOa?JkSjl/juloIa38-JLYraYn2xRx!w96x?fvDh)g?571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 29,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 30,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:38",
          "constructive_proposal": true,
          "lane_root_hash72": "G*WUcw+r-JtH/3oULm6kf*QbG<6d6C-x(!c!?Mv8fj+Ud!J3Y+gsfuEG+zHwNgK8qV!OQ7N/",
          "phase_state": "zw",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 29,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 30,
        "transition_admitted": true,
        "transition_root_hash72": "8480ZnZwEH!3v-5XifWMktTT7AF1Nb4+!M51cLaskmkM-VB7RtaWhVwqMZhDPxHOK/GAEVOK",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:38"
          ],
          "cell_id": "cell:38",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 30,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")YaxG2ZrjMI)Ic!1e3VSUnPu-MT?jNHmjLW5Ai0PJjO?MOY6EAJaQtH/dTjX4yLMQRT?+y5t",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 29,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:39",
      "cell_identity_count": 1,
      "cell_root_hash72": "r7uKsFSE0TQtYOGusZ4(MF1pQ3lX>w*BOxk>I4L4k1+xDVdq>iqyZTbjYnWv-Q8zQQ*E)HaZ",
      "column": 3,
      "domain_id": "PROVENANCE_AUDIT",
      "energy_credit": 15,
      "global_index": 39,
      "lane_count": 3,
      "lo_shu_value": 3,
      "phase_tensor": "w",
      "proposed_energy_credit": 13,
      "row": 4,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:4",
      "transition": {
        "admitted_energy": 15,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:39",
        "current_phase": "wz",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "x",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:39",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwL?xRsaA4kpW<5srpQ>FOa?JkSjl/jvkoIa38-JLYraYn2vYs!w96x?fvDh(b5571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 13,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 15,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:39",
          "constructive_proposal": true,
          "lane_root_hash72": "/IT0z/PMTnwQKYGa?V9ktdY3)>7+LhjsKw721NueyKrXNbKjZD)mGWvfWZV0557DbmkIyEH5",
          "phase_state": "wz",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 13,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 15,
        "transition_admitted": true,
        "transition_root_hash72": "+SdwFBs<fHfz08Y-Mq(LKxblocZL!c(xi+jRknICcy6XVD9SDxVURxfD+bDZ3WF59yj-aJ7T",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:39"
          ],
          "cell_id": "cell:39",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 15,
          "correction_applied": {
            "denominator": 1,
            "numerator": 2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")WhsH1ZrjMI)Ic!1e3VSUnPu-LO5jNHmjLW5Ai0PJjO?MOY6FzJaQtI*dTjX4yLMQRT?+z4t",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "proposed_energy": 13,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:40",
      "cell_identity_count": 1,
      "cell_root_hash72": "kRwrOz-Jvq(AwrM72iehaaZ2hsfGWX8lpH9H)732dm4Eh(xMHx*sTkV3YW5C6IpE34hDQYP6",
      "column": 4,
      "domain_id": "PROVENANCE_AUDIT",
      "energy_credit": 25,
      "global_index": 40,
      "lane_count": 3,
      "lo_shu_value": 5,
      "phase_tensor": "x",
      "proposed_energy_credit": 25,
      "row": 4,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:4",
      "transition": {
        "admitted_energy": 25,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:40",
        "current_phase": "x",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "y",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:40",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKjqj5<7ji5wSCe(l<LJ1RXP(>tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 25,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 25,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:40",
          "constructive_proposal": true,
          "lane_root_hash72": "BFaNFvrAQ8WmUQnJ6?tvexoSHC0(ab1l*CHndcGHM7clpZPaQPjfeDt!0h)lMFwFnY41vMn5",
          "phase_state": "x",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 25,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 25,
        "transition_admitted": true,
        "transition_root_hash72": "Q0QmJN8hjOAq7tuAZKVc?5tvq4Kom57R9thnGIzFiunErWk<RxsZ4mIdVG?u3jBfCEMw9xEv",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:40",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 25,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zV0dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*ya+vRgVFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 25,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:41",
      "cell_identity_count": 1,
      "cell_root_hash72": "EZ(/C7rILVs+sHY7N!>qgfy+T0mYuu93(BYG(saYhCfFl!shva<OM/bYrXCI/TC14/0)ZlYc",
      "column": 5,
      "domain_id": "PROVENANCE_AUDIT",
      "energy_credit": 35,
      "global_index": 41,
      "lane_count": 3,
      "lo_shu_value": 7,
      "phase_tensor": "y",
      "proposed_energy_credit": 37,
      "row": 4,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:4",
      "transition": {
        "admitted_energy": 35,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:41",
        "current_phase": "y",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "z",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:41",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bScbqpYhZ7VQWsg4/NqX>2QuGWU(!EsfI>UD/vTL>827yUjN!SRCg7qQc5Mo90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 37,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 35,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:41",
          "constructive_proposal": true,
          "lane_root_hash72": "UdGeo6CGX<a/5-LqYvXd9TBQd2G8ctX/Mf9?x6/M1D?<DaC3UAaWTxF6Qlvk)(Hr>3q75f-o",
          "phase_state": "y",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 37,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 35,
        "transition_admitted": true,
        "transition_root_hash72": "?V9L3tve71ky+mck)U8lZUC+q/BhQN3sQ1<Ty5epOsccO2CA*CzKJa7rIwt6vkPYDC9Z!7t9",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:41"
          ],
          "cell_id": "cell:41",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 35,
          "correction_applied": {
            "denominator": 1,
            "numerator": -2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G6>xJ6VH!Yjtu5QR+XZ3rMzy5GG/sQUb03FcOUwo>eswrvjhlABiTvuc/84-KbvF-iuRRRt9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "proposed_energy": 37,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:42",
      "cell_identity_count": 1,
      "cell_root_hash72": "RPNaww+k8ngjfN2L*5zN9E-Myj0!uh5qWYisxuOs?n6ZNwD2vuv3PCj7UIDHaSHdSEbdQgQA",
      "column": 6,
      "domain_id": "PROVENANCE_AUDIT",
      "energy_credit": 20,
      "global_index": 42,
      "lane_count": 3,
      "lo_shu_value": 4,
      "phase_tensor": "z",
      "proposed_energy_credit": 21,
      "row": 4,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:4",
      "transition": {
        "admitted_energy": 20,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:42",
        "current_phase": "z",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "w",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:42",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU(!FrfI>UD/vTL>827xQoN!SRCg7qQc4Hu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 21,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 20,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:42",
          "constructive_proposal": true,
          "lane_root_hash72": "8dH9JvGQW71/HY?8QJnjI*QCqN+zd<X5>4nrYX-iTXA3Tyk)RftNU703(h+qSXR4Dv7O(D0g",
          "phase_state": "z",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 21,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 20,
        "transition_admitted": true,
        "transition_root_hash72": ")cq8g-pD*/u3N0?LbR5)luFtAW90wGZ4(ws1shNOk/iFyc>nf49KLXLQ4VEXtTk60oz2Ib30",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:42"
          ],
          "cell_id": "cell:42",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 20,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G5/CI7VH!Yjtu5QR+XZ3rMzy5FB?sQUb03FcOUwo>eswrvjhmzBiTvub(84-KbvF-iuRRSs9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 21,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:43",
      "cell_identity_count": 1,
      "cell_root_hash72": "yV/LCbKmdLJWiRg1hFqUd<pLYk6rgOnBFdLgsChsVVG(nhA4V-?uSQ)LXRtS)Cj9<RgSxHwA",
      "column": 7,
      "domain_id": "PROVENANCE_AUDIT",
      "energy_credit": 45,
      "global_index": 43,
      "lane_count": 3,
      "lo_shu_value": 9,
      "phase_tensor": "w",
      "proposed_energy_credit": 45,
      "row": 4,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:4",
      "transition": {
        "admitted_energy": 45,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:43",
        "current_phase": "w",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "xy",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:43",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKjtg5<7ji5yQCe(l<LJ1RXP<)tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 45,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 45,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:43",
          "constructive_proposal": true,
          "lane_root_hash72": "YaXw6j+JAaaKs6pwfMnx/0I+rOF4*pSVv?rwQ*<BanDD<zA<t(n4c!J!kvvSGmbZ4R1wrxcD",
          "phase_state": "w",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 45,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 45,
        "transition_admitted": true,
        "transition_root_hash72": "YQferegqIyzmpYbXhTFJv<K*Lc8IxoX+pM71llYvF!DjlTiDXR!n73N2J0fE93gT5rPgt(<O",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:43",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 45,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zX!dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*ydYvRiTFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 45,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:44",
      "cell_identity_count": 1,
      "cell_root_hash72": "IDJGOQ4iuWyo0zp7)eTHWJKpUYSo+R7IM6sFMcP+UcWe-KugYy2mWCmhlmEoIg8st)9!BF5(",
      "column": 8,
      "domain_id": "PROVENANCE_AUDIT",
      "energy_credit": 10,
      "global_index": 44,
      "lane_count": 3,
      "lo_shu_value": 2,
      "phase_tensor": "x",
      "proposed_energy_credit": 9,
      "row": 4,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:4",
      "transition": {
        "admitted_energy": 10,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:44",
        "current_phase": "xy",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "yx",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:44",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "+c6!S2t8XiE/VvfLaJRX)If8-UTHB(j4mUU>yB02Mta3Dr-FDQrik2qcxRBxDJq-d!ff*rZN",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 9,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 10,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:44",
          "constructive_proposal": true,
          "lane_root_hash72": "vlenQs+cKDusmgg8cMwqrylTWd)mBz5La/Ki/7QYEcbwvE0y3-QiRY0?WFHAJ5yV+FrL3IWg",
          "phase_state": "xy",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 9,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 10,
        "transition_admitted": true,
        "transition_root_hash72": "zcgcvFOjGvyHyEi6/j4UuuCTdQ9-cS0OYdQKVBhVn!?R5l/NRVu-FlAYC/MUUlHr6JWCN4gp",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:44"
          ],
          "cell_id": "cell:44",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 10,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "9zZVuHr1)RL72NV>c5SMCp*Ej2jp+yoTsuwMWbMu2?5912N5-9tIXbD4gt-flYKoTTqQ1Jz7",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 9,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:45",
      "cell_identity_count": 1,
      "cell_root_hash72": "2ZAD+zi1VYa4?2oyC?Zp07e9whH0aqcjDBYv2db?W*Yxf72zx?B4kx8v*TT/-sHceDYv-ir/",
      "column": 0,
      "domain_id": "MULTIMODAL_FUSION",
      "energy_credit": 40,
      "global_index": 45,
      "lane_count": 3,
      "lo_shu_value": 8,
      "phase_tensor": "y",
      "proposed_energy_credit": 41,
      "row": 5,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:5",
      "transition": {
        "admitted_energy": 40,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:45",
        "current_phase": "yx",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "zw",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:45",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU(!IofI>UD/vTL>827zOoN!SRCg7qQc6Fu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 41,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 40,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:45",
          "constructive_proposal": true,
          "lane_root_hash72": "OEWThbCnQKiQ/Bqw/u*U9tH<UTv*PBnxSNnUGoMbJBHj6Sll<(B9ot(b(lL0IpV>NfG>9ipT",
          "phase_state": "yx",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 41,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 40,
        "transition_admitted": true,
        "transition_root_hash72": "zhj!Fji5VcAQhL>rGRM>7mfJczWa8GvAqFk0?3IYg-pUc+nEltHi1gF24XhHmjD0XKUnzdzr",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:45"
          ],
          "cell_id": "cell:45",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 40,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G7+CI7VH!Yjtu5QR+XZ3rMzy5Hz?sQUb03FcOUwo>eswrvjhpwBiTvub(84-KbvF-iuRRVp9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 41,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:46",
      "cell_identity_count": 1,
      "cell_root_hash72": "SG?c9>9/<U?k5>KD52G5R+enYndY)V47*JX4mbd3qDhv6WjqHP9Y2!DRa3VJx>XHOFn71es*",
      "column": 1,
      "domain_id": "MULTIMODAL_FUSION",
      "energy_credit": 5,
      "global_index": 46,
      "lane_count": 3,
      "lo_shu_value": 1,
      "phase_tensor": "z",
      "proposed_energy_credit": 5,
      "row": 5,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:5",
      "transition": {
        "admitted_energy": 5,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:46",
        "current_phase": "zw",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "wz",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:46",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "l6Mnaw8gg4A5SI/9YFbvqzEn!Dkcb7Cvz)rIAWVMvFVmLy)YJJR3I!35acXqMy76JV2!It6u",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 5,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 5,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:46",
          "constructive_proposal": true,
          "lane_root_hash72": "G*WUcw+r-JtH/3oULm6kf*QbG<6d6C-x(!c!?Mv8fj+Ud!J3Y+gsfuEG+zHwOdM8qV!OQ7N/",
          "phase_state": "zw",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 5,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 5,
        "transition_admitted": true,
        "transition_root_hash72": "<4hNRRieJtM(62bH93TVAKjKZEJ?o*NSLYw9PIVhTSvb+IXl!trI6EFLgc+zUjpeJ/H?7/WO",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:46",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 5,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "DW1i*Y1i9k1>-hVz(qM!Ip6*f-t6g*P-Eq7D0NQo3b2B6VCAazqaFlT55GsN3>LZCT>HI7Wh",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 5,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:47",
      "cell_identity_count": 1,
      "cell_root_hash72": "KKv</m58FnFUK!2Nlon<MJw4Xpriw+m-U7GoiB1Jt3-PMUB7euvA7RkDT>Q2<p9>vzf>g8Ce",
      "column": 2,
      "domain_id": "MULTIMODAL_FUSION",
      "energy_credit": 30,
      "global_index": 47,
      "lane_count": 3,
      "lo_shu_value": 6,
      "phase_tensor": "w",
      "proposed_energy_credit": 29,
      "row": 5,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:5",
      "transition": {
        "admitted_energy": 30,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:47",
        "current_phase": "wz",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "x",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:47",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwK0xRsaA4kpW<5srpQ>FOa?JkSjl/ksmoIa38-JLYraYn2xRx!w96x?fvDh)g?571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 29,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 30,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:47",
          "constructive_proposal": true,
          "lane_root_hash72": "/IT0z/PMTnwQKYGa?V9ktdY3)>7+LhjsKw721NueyKrXNbKjZD)mGWvfWZV0629DbmkIyEH5",
          "phase_state": "wz",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 29,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 30,
        "transition_admitted": true,
        "transition_root_hash72": "<QdwFDt9?Hfz?eTZNq(MGC9lofPN5b+Ba87TngQxcy6WWD9SDyZZHxfE>av+3WH>2Go-aI9P",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:47"
          ],
          "cell_id": "cell:47",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 30,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")YaxG2ZrjMI)Ic!1e3VSUnPu-MT?jNHmjLW5Ai0PJjO?MOY7CBJaQtH/dTjX4yLMQRT?*w6t",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 29,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:48",
      "cell_identity_count": 1,
      "cell_root_hash72": "p>9+2f(7CM>VDke9(2CBLv6aa*E4Dh7+sCUuqvmIM?e3)yfMFbuw?+wW4?*IvQy2oB+Ro7gO",
      "column": 3,
      "domain_id": "MULTIMODAL_FUSION",
      "energy_credit": 15,
      "global_index": 48,
      "lane_count": 3,
      "lo_shu_value": 3,
      "phase_tensor": "x",
      "proposed_energy_credit": 13,
      "row": 5,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:5",
      "transition": {
        "admitted_energy": 15,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:48",
        "current_phase": "x",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "y",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:48",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwL?xRsaA4kpW<5srpQ>FOa?JkSjl/ktloIa38-JLYraYn2vYs!w96x?fvDh(b5571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 13,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 15,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:48",
          "constructive_proposal": true,
          "lane_root_hash72": "BFaNFvrAQ8WmUQnJ6?tvexoSHC0(ab1l*CHndcGHM7clpZPaQPjfeDt!0h)lMNoFnY41vMn5",
          "phase_state": "x",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 13,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 15,
        "transition_admitted": true,
        "transition_root_hash72": "tVyjt5x/kyFIFfTCNzS4oj4JZaDwL0W2XyW!noFqKvt>tbk0by6yY3nL+miKu21W28Z6bAE!",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:48"
          ],
          "cell_id": "cell:48",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 15,
          "correction_applied": {
            "denominator": 1,
            "numerator": 2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")WhsH1ZrjMI)Ic!1e3VSUnPu-LO5jNHmjLW5Ai0PJjO?MOY7DAJaQtI*dTjX4yLMQRT?*x5t",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "proposed_energy": 13,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:49",
      "cell_identity_count": 1,
      "cell_root_hash72": "c9nxhO>cz9hAJ0V/r92i<T4<U>W*XbiBvhGqyG3JVZ28>T*?<*B0Dbx0rN4Czv)Z9H-j84rJ",
      "column": 4,
      "domain_id": "MULTIMODAL_FUSION",
      "energy_credit": 25,
      "global_index": 49,
      "lane_count": 3,
      "lo_shu_value": 5,
      "phase_tensor": "y",
      "proposed_energy_credit": 25,
      "row": 5,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:5",
      "transition": {
        "admitted_energy": 25,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:49",
        "current_phase": "y",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "z",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:49",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKjza5<7ji5wSCe(l<LJ1RXP(>tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 25,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 25,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:49",
          "constructive_proposal": true,
          "lane_root_hash72": "UdGeo6CGX<a/5-LqYvXd9TBQd2G8ctX/Mf9?x6/M1D?<DaC3UAaWTxF6Qlvk)2zr>3q75f-o",
          "phase_state": "y",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 25,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 25,
        "transition_admitted": true,
        "transition_root_hash72": "3ErsbDoq01PydowgEdtQSChTNyY/2VW1f*c*WoCsQeZs3VamLmcgNTZt3>MUPo8CNx?+K2mv",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:49",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 25,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zV0dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*yjSvRgVFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 25,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:50",
      "cell_identity_count": 1,
      "cell_root_hash72": "Soe4gIE*55knGJVX*BRlG<z+dXg)/Nb?GpxdV58Cmk>82Exl8+Sn!v-Vjkq6tXe(F>svH<n<",
      "column": 5,
      "domain_id": "MULTIMODAL_FUSION",
      "energy_credit": 35,
      "global_index": 50,
      "lane_count": 3,
      "lo_shu_value": 7,
      "phase_tensor": "z",
      "proposed_energy_credit": 37,
      "row": 5,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:5",
      "transition": {
        "admitted_energy": 35,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:50",
        "current_phase": "z",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "w",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:50",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bScbqpYhZ7VQWsg4/NqX>2QuGWU(?CtfI>UD/vTL>827yUjN!SRCg7qQc5Mo90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 37,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 35,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:50",
          "constructive_proposal": true,
          "lane_root_hash72": "8dH9JvGQW71/HY?8QJnjI*QCqN+zd<X5>4nrYX-iTXA3Tyk)RftNU703(h+qTUT4Dv7O(D0g",
          "phase_state": "z",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 37,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 35,
        "transition_admitted": true,
        "transition_root_hash72": ")cqah39D*/u4U*?LbbI0juGxxPh<vK8AexyYxhNOk(hFyc!r4a9KLYQsnZzYxOm8<oz2J87!",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:50"
          ],
          "cell_id": "cell:50",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 35,
          "correction_applied": {
            "denominator": 1,
            "numerator": -2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G6>xJ6VH!Yjtu5QR+XZ3rMzy5GG/sQUb03FcOUwo>eswrvjijBBiTvuc/84-KbvF-iuRSPu9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "proposed_energy": 37,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:51",
      "cell_identity_count": 1,
      "cell_root_hash72": "/BY1aY6VbHccj*(kXt(xznVdGm(QTqke!rKzhCLF-STs9kJer?7xbsm<82bN>Aj99b!Tp?om",
      "column": 6,
      "domain_id": "MULTIMODAL_FUSION",
      "energy_credit": 20,
      "global_index": 51,
      "lane_count": 3,
      "lo_shu_value": 4,
      "phase_tensor": "w",
      "proposed_energy_credit": 21,
      "row": 5,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:5",
      "transition": {
        "admitted_energy": 20,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:51",
        "current_phase": "w",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "xy",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:51",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU(?DsfI>UD/vTL>827xQoN!SRCg7qQc4Hu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 21,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 20,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:51",
          "constructive_proposal": true,
          "lane_root_hash72": "YaXw6j+JAaaKs6pwfMnx/0I+rOF4*pSVv?rwQ*<BanDD<zA<t(n4c!J!kvvSHjdZ4R1wrxcD",
          "phase_state": "w",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 21,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 20,
        "transition_admitted": true,
        "transition_root_hash72": "2<10uz/4**WW!<PVJDmWVU+!Mb7PhKm4ZDJ11f*)sXjbD8Xb57+YIx>L1OwcDF-TbbmyAbMx",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:51"
          ],
          "cell_id": "cell:51",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 20,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G5/CI7VH!Yjtu5QR+XZ3rMzy5FB?sQUb03FcOUwo>eswrvjikABiTvub(84-KbvF-iuRSQt9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 21,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:52",
      "cell_identity_count": 1,
      "cell_root_hash72": "wM?bA17(UKeYEO3gNw8NgDRFLx-iv)ullmGny>XxIH6/T<CMR++02yzDgNIgnszg)9*>X1ss",
      "column": 7,
      "domain_id": "MULTIMODAL_FUSION",
      "energy_credit": 45,
      "global_index": 52,
      "lane_count": 3,
      "lo_shu_value": 9,
      "phase_tensor": "x",
      "proposed_energy_credit": 45,
      "row": 5,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:5",
      "transition": {
        "admitted_energy": 45,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:52",
        "current_phase": "xy",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "yx",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:52",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKkrh5<7ji5yQCe(l<LJ1RXP<)tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 45,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 45,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:52",
          "constructive_proposal": true,
          "lane_root_hash72": "vlenQs+cKDusmgg8cMwqrylTWd)mBz5La/Ki/7QYEcbwvE0y3-QiRY0?WFHAK2AV+FrL3IWg",
          "phase_state": "xy",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 45,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 45,
        "transition_admitted": true,
        "transition_root_hash72": "D5UI/HxQCUpQ2DwwEENebMEp3ZNCiZQ6OUxQgPqr7Go7v0>ejH2-Wrnca>a*e>BV<)8mYCKy",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:52",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 45,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zX!dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*zbZvRiTFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 45,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:53",
      "cell_identity_count": 1,
      "cell_root_hash72": "e>QA>rmUt1)g3PvuP*OqcjlDsRFS954SH4R-7hiMqY>sPT!pEMqeUehTb3ZpHno6K6CoT4Z9",
      "column": 8,
      "domain_id": "MULTIMODAL_FUSION",
      "energy_credit": 10,
      "global_index": 53,
      "lane_count": 3,
      "lo_shu_value": 2,
      "phase_tensor": "y",
      "proposed_energy_credit": 9,
      "row": 5,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:5",
      "transition": {
        "admitted_energy": 10,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:53",
        "current_phase": "yx",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "zw",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:53",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "+c6!S2t8XiE/VvfLaJRX)If8-UTHB(j5kVU>yB02Mta3Dr-FDQrik2qcxRBxDJq-d!ff*rZN",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 9,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 10,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:53",
          "constructive_proposal": true,
          "lane_root_hash72": "OEWThbCnQKiQ/Bqw/u*U9tH<UTv*PBnxSNnUGoMbJBHj6Sll<(B9ot(b(lL0JmX>NfG>9ipT",
          "phase_state": "yx",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 9,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 10,
        "transition_admitted": true,
        "transition_root_hash72": "p9rQOPiWhjIpSO8A4GF?en?PIb30Hs*ASVZ8iXdQ<G4>OxLjH3-n)W>QX5lMkrfI-Y8g!uIf",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:53"
          ],
          "cell_id": "cell:53",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 10,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "9zZVuHr1)RL72NV>c5SMCp*Ej2jp+yoTsuwMWbMu2?5912N6YatIXbD4gt-flYKoTTqQ2HA7",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 9,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:54",
      "cell_identity_count": 1,
      "cell_root_hash72": "Ygpr(Q43hp(FoQ0n2tf*Jd1W7TGM79EN89J7KSyhFPqd5yJ940DwgLIJEw0k*qjcSaBa<fu)",
      "column": 0,
      "domain_id": "CONSTRAINT_TOPOLOGY",
      "energy_credit": 40,
      "global_index": 54,
      "lane_count": 3,
      "lo_shu_value": 8,
      "phase_tensor": "z",
      "proposed_energy_credit": 41,
      "row": 6,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:6",
      "transition": {
        "admitted_energy": 40,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:54",
        "current_phase": "zw",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "wz",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:54",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU(?GpfI>UD/vTL>827zOoN!SRCg7qQc6Fu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 41,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 40,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:54",
          "constructive_proposal": true,
          "lane_root_hash72": "G*WUcw+r-JtH/3oULm6kf*QbG<6d6C-x(!c!?Mv8fj+Ud!J3Y+gsfuEG+zHwPaO8qV!OQ7N/",
          "phase_state": "zw",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 41,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 40,
        "transition_admitted": true,
        "transition_root_hash72": "GtPjV0OS<mtD7V6DaUthYInGK*/?PDMwji5>M3f7jy1JL/w9Af1A+gLr-/aZJ*S2D-ftCFLf",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:54"
          ],
          "cell_id": "cell:54",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 40,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G7+CI7VH!Yjtu5QR+XZ3rMzy5Hz?sQUb03FcOUwo>eswrvjinxBiTvub(84-KbvF-iuRSTq9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 41,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:55",
      "cell_identity_count": 1,
      "cell_root_hash72": "t9J5VVB3?VhntFgIuJ/fO>lB)y/Ztz0/rq0k7Df<L3PZgBrkmdgTkFsbhMlCYk77)dwH<AqL",
      "column": 1,
      "domain_id": "CONSTRAINT_TOPOLOGY",
      "energy_credit": 5,
      "global_index": 55,
      "lane_count": 3,
      "lo_shu_value": 1,
      "phase_tensor": "w",
      "proposed_energy_credit": 5,
      "row": 6,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:6",
      "transition": {
        "admitted_energy": 5,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:55",
        "current_phase": "wz",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "x",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:55",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "l6Mnaw8gg4A5SI/9YFbvqzEn!Dkcb7Cwx<rIAWVMvFVmLy)YJJR3I!35acXqMy76JV2!It6u",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 5,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 5,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:55",
          "constructive_proposal": true,
          "lane_root_hash72": "/IT0z/PMTnwQKYGa?V9ktdY3)>7+LhjsKw721NueyKrXNbKjZD)mGWvfWZV07?bDbmkIyEH5",
          "phase_state": "wz",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 5,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 5,
        "transition_admitted": true,
        "transition_root_hash72": "r3Y7TKUD(d<epi*6LqFOvwkAOcFJ2E9vmnm-OSHr6x/Utt0QU-a50Mt+wXLTQbNZ<lCA9wZz",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:55",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 5,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "DW1i*Y1i9k1>-hVz(qM!Ip6*f-t6g*P-Eq7D0NQo3b2B6VCAazqaFlT55GsO1!LZCT>HI7Wh",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 5,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:56",
      "cell_identity_count": 1,
      "cell_root_hash72": "Pz82B1glHyKAHN0!bU!UmTqU0KEB8A)ehzRlrgm/z0yo0xmBgeQbj51UytLEJJJ8AeA5RPYN",
      "column": 2,
      "domain_id": "CONSTRAINT_TOPOLOGY",
      "energy_credit": 30,
      "global_index": 56,
      "lane_count": 3,
      "lo_shu_value": 6,
      "phase_tensor": "x",
      "proposed_energy_credit": 29,
      "row": 6,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:6",
      "transition": {
        "admitted_energy": 30,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:56",
        "current_phase": "x",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "y",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:56",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwK0xRsaA4kpW<5srpQ>FOa?JkSjl/lqnoIa38-JLYraYn2xRx!w96x?fvDh)g?571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 29,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 30,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:56",
          "constructive_proposal": true,
          "lane_root_hash72": "BFaNFvrAQ8WmUQnJ6?tvexoSHC0(ab1l*CHndcGHM7clpZPaQPjfeDt!0h)lNKqFnY41vMn5",
          "phase_state": "x",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 29,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 30,
        "transition_admitted": true,
        "transition_root_hash72": "rVykqfp/kyEOAeUCNzT0th4LY4LrO?QjLAX2aAAqKuu>tbk0cCboY4rRQhnKw)5KadZ6aCA3",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:56"
          ],
          "cell_id": "cell:56",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 30,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")YaxG2ZrjMI)Ic!1e3VSUnPu-MT?jNHmjLW5Ai0PJjO?MOY8ACJaQtH/dTjX4yLMQRT?/u7t",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 29,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:57",
      "cell_identity_count": 1,
      "cell_root_hash72": ")MbNL<q!jMSQs-YE(De-wB)T0EYQ!gsoNbwvYvN>Dkk26TBV/i)QX779)t<NF0Zu?t!ZodzF",
      "column": 3,
      "domain_id": "CONSTRAINT_TOPOLOGY",
      "energy_credit": 15,
      "global_index": 57,
      "lane_count": 3,
      "lo_shu_value": 3,
      "phase_tensor": "y",
      "proposed_energy_credit": 13,
      "row": 6,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:6",
      "transition": {
        "admitted_energy": 15,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:57",
        "current_phase": "y",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "z",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:57",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwL?xRsaA4kpW<5srpQ>FOa?JkSjl/lrmoIa38-JLYraYn2vYs!w96x?fvDh(b5571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 13,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 15,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:57",
          "constructive_proposal": true,
          "lane_root_hash72": "UdGeo6CGX<a/5-LqYvXd9TBQd2G8ctX/Mf9?x6/M1D?<DaC3UAaWTxF6Qlvk<?Br>3q75f-o",
          "phase_state": "y",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 13,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 15,
        "transition_admitted": true,
        "transition_root_hash72": "!8/V)-w7tNLavv*j0OSpdkUoyJccaNkphDsV43Zw9q!dad7q30(9Y/MHO7Jj+jh4tVfSgqNs",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:57"
          ],
          "cell_id": "cell:57",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 15,
          "correction_applied": {
            "denominator": 1,
            "numerator": 2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")WhsH1ZrjMI)Ic!1e3VSUnPu-LO5jNHmjLW5Ai0PJjO?MOY8BBJaQtI*dTjX4yLMQRT?/v6t",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "proposed_energy": 13,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:58",
      "cell_identity_count": 1,
      "cell_root_hash72": "s<0av<DfoE)jIIcuSL>IQtDB6umvK7ywX6V-11JU)M!)/cr0>9x5myvJnAyUphR4iLD2p7/Y",
      "column": 4,
      "domain_id": "CONSTRAINT_TOPOLOGY",
      "energy_credit": 25,
      "global_index": 58,
      "lane_count": 3,
      "lo_shu_value": 5,
      "phase_tensor": "z",
      "proposed_energy_credit": 25,
      "row": 6,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:6",
      "transition": {
        "admitted_energy": 25,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:58",
        "current_phase": "z",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "w",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:58",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKkxb5<7ji5wSCe(l<LJ1RXP(>tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 25,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 25,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:58",
          "constructive_proposal": true,
          "lane_root_hash72": "8dH9JvGQW71/HY?8QJnjI*QCqN+zd<X5>4nrYX-iTXA3Tyk)RftNU703(h+qT*L4Dv7O(D0g",
          "phase_state": "z",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 25,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 25,
        "transition_admitted": true,
        "transition_root_hash72": "P<bkl9h<Xs<sc?+-ITyHtk)QSHlnHZVdOhSu+RpAa520KYc1ip-JTB+XKh5G5BTWm8)i+AD3",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:58",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 25,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zV0dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*zhTvRgVFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 25,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:59",
      "cell_identity_count": 1,
      "cell_root_hash72": "X6+/6yv9TdgKVmmFW9uFv/dYxu84Hblf/b*-z>dNxGI7N8gq5UKp+7k1wHKP<C2ZUd*Bicc-",
      "column": 5,
      "domain_id": "CONSTRAINT_TOPOLOGY",
      "energy_credit": 35,
      "global_index": 59,
      "lane_count": 3,
      "lo_shu_value": 7,
      "phase_tensor": "w",
      "proposed_energy_credit": 37,
      "row": 6,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:6",
      "transition": {
        "admitted_energy": 35,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:59",
        "current_phase": "w",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "xy",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:59",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bScbqpYhZ7VQWsg4/NqX>2QuGWU(?LkfI>UD/vTL>827yUjN!SRCg7qQc5Mo90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 37,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 35,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:59",
          "constructive_proposal": true,
          "lane_root_hash72": "YaXw6j+JAaaKs6pwfMnx/0I+rOF4*pSVv?rwQ*<BanDD<zA<t(n4c!J!kvvSHr5Z4R1wrxcD",
          "phase_state": "w",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 37,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 35,
        "transition_admitted": true,
        "transition_root_hash72": "N<10vMtq**WW?3HVJDm(F*+?Q6nzhSgnlXJiOk*)sXkaD8Xc9<>YIx!PZ-rcEJVVd7myAbVN",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:59"
          ],
          "cell_id": "cell:59",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 35,
          "correction_applied": {
            "denominator": 1,
            "numerator": -2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G6>xJ6VH!Yjtu5QR+XZ3rMzy5GG/sQUb03FcOUwo>eswrvjissBiTvuc/84-KbvF-iuRSYl9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "proposed_energy": 37,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:60",
      "cell_identity_count": 1,
      "cell_root_hash72": "FOU+2Uk+<QHn7<A0YrM!wgts0ioc9AEfnwdJYT8?OjdGbp0AyJB6W*In(T/Q(0u7w9ZLn?*i",
      "column": 6,
      "domain_id": "CONSTRAINT_TOPOLOGY",
      "energy_credit": 20,
      "global_index": 60,
      "lane_count": 3,
      "lo_shu_value": 4,
      "phase_tensor": "x",
      "proposed_energy_credit": 21,
      "row": 6,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:6",
      "transition": {
        "admitted_energy": 20,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:60",
        "current_phase": "xy",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "yx",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:60",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU(0BtfI>UD/vTL>827xQoN!SRCg7qQc4Hu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 21,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 20,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:60",
          "constructive_proposal": true,
          "lane_root_hash72": "vlenQs+cKDusmgg8cMwqrylTWd)mBz5La/Ki/7QYEcbwvE0y3-QiRY0?WFHAL?CV+FrL3IWg",
          "phase_state": "xy",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 21,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 20,
        "transition_admitted": true,
        "transition_root_hash72": "W08unOOZA5q!>B7>vub>2CQMR3>1BbpUs57BELR/HikEDPF!tf9VLP8aQ)mUWd/V1xyJeXaF",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:60"
          ],
          "cell_id": "cell:60",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 20,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G5/CI7VH!Yjtu5QR+XZ3rMzy5FB?sQUb03FcOUwo>eswrvjjiBBiTvub(84-KbvF-iuRTOu9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 21,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:61",
      "cell_identity_count": 1,
      "cell_root_hash72": "uZu+LtFC*Eex6m6WapodTHgG>poU>6q8u>SNRZgervvw5??IhlqnYry+)kKc4LoCz1f?!m(w",
      "column": 7,
      "domain_id": "CONSTRAINT_TOPOLOGY",
      "energy_credit": 45,
      "global_index": 61,
      "lane_count": 3,
      "lo_shu_value": 9,
      "phase_tensor": "y",
      "proposed_energy_credit": 45,
      "row": 6,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:6",
      "transition": {
        "admitted_energy": 45,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:61",
        "current_phase": "yx",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "zw",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:61",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKlpi5<7ji5yQCe(l<LJ1RXP<)tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 45,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 45,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:61",
          "constructive_proposal": true,
          "lane_root_hash72": "OEWThbCnQKiQ/Bqw/u*U9tH<UTv*PBnxSNnUGoMbJBHj6Sll<(B9ot(b(lL0KjZ>NfG>9ipT",
          "phase_state": "yx",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 45,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 45,
        "transition_admitted": true,
        "transition_root_hash72": "bcKM?!R-seA3EPir!B8I6Jc?)LI9qnfrKP6ol)?C+ahm*ylROAm4ujXiSe(7ALWboVUx?6*1",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:61",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 45,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zX!dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*A9-vRiTFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 45,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:62",
      "cell_identity_count": 1,
      "cell_root_hash72": "4-69zQBeeCE+so1e6ZvJAK)eRFe2HTSH-SabMomdx6KRh->0U*BHNo(xzhv-DI)M?w+Kb/h-",
      "column": 8,
      "domain_id": "CONSTRAINT_TOPOLOGY",
      "energy_credit": 10,
      "global_index": 62,
      "lane_count": 3,
      "lo_shu_value": 2,
      "phase_tensor": "z",
      "proposed_energy_credit": 9,
      "row": 6,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:6",
      "transition": {
        "admitted_energy": 10,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:62",
        "current_phase": "zw",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "wz",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:62",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "+c6!S2t8XiE/VvfLaJRX)If8-UTHB(j6iWU>yB02Mta3Dr-FDQrik2qcxRBxDJq-d!ff*rZN",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 9,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 10,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:62",
          "constructive_proposal": true,
          "lane_root_hash72": "G*WUcw+r-JtH/3oULm6kf*QbG<6d6C-x(!c!?Mv8fj+Ud!J3Y+gsfuEG+zHwQ7Q8qV!OQ7N/",
          "phase_state": "zw",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 9,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 10,
        "transition_admitted": true,
        "transition_root_hash72": "?lX1)tQBpuBcIYhMIJmZsDbL6F7+gmawLyK6*-T??eQWdzUYWZkFVW35K8h/H0uKG4Dm1WUA",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:62"
          ],
          "cell_id": "cell:62",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 10,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "9zZVuHr1)RL72NV>c5SMCp*Ej2jp+yoTsuwMWbMu2?5912N7WbtIXbD4gt-flYKoTTqQ3FB7",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 9,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:63",
      "cell_identity_count": 1,
      "cell_root_hash72": "K!Ro7oy-JKWCR!etupuA?gahT*9)6THq9(BBMnNiX9vI?1jcpXS4VPnZn82ckg6D*cU4Es/p",
      "column": 0,
      "domain_id": "INFORMATION_ENERGY",
      "energy_credit": 40,
      "global_index": 63,
      "lane_count": 3,
      "lo_shu_value": 8,
      "phase_tensor": "w",
      "proposed_energy_credit": 41,
      "row": 7,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:7",
      "transition": {
        "admitted_energy": 40,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:63",
        "current_phase": "wz",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "x",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:63",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU(0EqfI>UD/vTL>827zOoN!SRCg7qQc6Fu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 41,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 40,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:63",
          "constructive_proposal": true,
          "lane_root_hash72": "/IT0z/PMTnwQKYGa?V9ktdY3)>7+LhjsKw721NueyKrXNbKjZD)mGWvfWZV08<dDbmkIyEH5",
          "phase_state": "wz",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 41,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 40,
        "transition_admitted": true,
        "transition_root_hash72": "2I>J*jMSOt61RlVhPQ488RJq?F02746HULPAPwng9*L74<7PZP33mgaqz7O<(6wp+/7My-yd",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:63"
          ],
          "cell_id": "cell:63",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 40,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G7+CI7VH!Yjtu5QR+XZ3rMzy5Hz?sQUb03FcOUwo>eswrvjjlyBiTvub(84-KbvF-iuRTRr9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 41,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:64",
      "cell_identity_count": 1,
      "cell_root_hash72": "hgKVE25H20ZCSwmuYDv*Qr+***P!rTXXu*Yt2<57rmVkBxs((*y66Xp)B*VhrQh4+oPI6dDp",
      "column": 1,
      "domain_id": "INFORMATION_ENERGY",
      "energy_credit": 5,
      "global_index": 64,
      "lane_count": 3,
      "lo_shu_value": 1,
      "phase_tensor": "x",
      "proposed_energy_credit": 5,
      "row": 7,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:7",
      "transition": {
        "admitted_energy": 5,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:64",
        "current_phase": "x",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "y",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:64",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "l6Mnaw8gg4A5SI/9YFbvqzEn!Dkcb7Cxv>rIAWVMvFVmLy)YJJR3I!35acXqMy76JV2!It6u",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 5,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 5,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:64",
          "constructive_proposal": true,
          "lane_root_hash72": "BFaNFvrAQ8WmUQnJ6?tvexoSHC0(ab1l*CHndcGHM7clpZPaQPjfeDt!0h)lOHsFnY41vMn5",
          "phase_state": "x",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 5,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 5,
        "transition_admitted": true,
        "transition_root_hash72": "s7pJs>+J-J?K6eAC5*f039ws-Xrm?fI3al(U5ogUuwF!1QWcLLM?k5o>Vj7!ava!nT6b3E/3",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:64",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 5,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "DW1i*Y1i9k1>-hVz(qM!Ip6*f-t6g*P-Eq7D0NQo3b2B6VCAazqaFlT55GsP??LZCT>HI7Wh",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 5,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:65",
      "cell_identity_count": 1,
      "cell_root_hash72": "7Nlnlq<dp5G9n+yfhL9T5QxV)0a>Tnww/szcp(vclew)90gTKw1*yOe?cuzgrHYKNq!G(CoV",
      "column": 2,
      "domain_id": "INFORMATION_ENERGY",
      "energy_credit": 30,
      "global_index": 65,
      "lane_count": 3,
      "lo_shu_value": 6,
      "phase_tensor": "y",
      "proposed_energy_credit": 29,
      "row": 7,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:7",
      "transition": {
        "admitted_energy": 30,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:65",
        "current_phase": "y",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "z",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:65",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwK0xRsaA4kpW<5srpQ>FOa?JkSjl/moooIa38-JLYraYn2xRx!w96x?fvDh)g?571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 29,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 30,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:65",
          "constructive_proposal": true,
          "lane_root_hash72": "UdGeo6CGX<a/5-LqYvXd9TBQd2G8ctX/Mf9?x6/M1D?<DaC3UAaWTxF6Qlvk><Dr>3q75f-o",
          "phase_state": "y",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 29,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 30,
        "transition_admitted": true,
        "transition_root_hash72": "<8/WOeo7tNKgqu/j0OTliiUqlPk7dMeG5FtZ+fUw9p?dad7q44??Y(QND2Oj/cl*B-fSftIx",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:65"
          ],
          "cell_id": "cell:65",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 30,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")YaxG2ZrjMI)Ic!1e3VSUnPu-MT?jNHmjLW5Ai0PJjO?MOY9yDJaQtH/dTjX4yLMQRT?(s8t",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 29,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:66",
      "cell_identity_count": 1,
      "cell_root_hash72": "SJ7m-Zr(b*kHDUaP7h3J?95T2wOZvD>mRJ2MkeaRMJVUPmR)G)7t/(6EvdZ/fu?omfu/w6Z1",
      "column": 3,
      "domain_id": "INFORMATION_ENERGY",
      "energy_credit": 15,
      "global_index": 66,
      "lane_count": 3,
      "lo_shu_value": 3,
      "phase_tensor": "z",
      "proposed_energy_credit": 13,
      "row": 7,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:7",
      "transition": {
        "admitted_energy": 15,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:66",
        "current_phase": "z",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "w",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:66",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwL?xRsaA4kpW<5srpQ>FOa?JkSjl/mpnoIa38-JLYraYn2vYs!w96x?fvDh(b5571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 13,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 15,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:66",
          "constructive_proposal": true,
          "lane_root_hash72": "8dH9JvGQW71/HY?8QJnjI*QCqN+zd<X5>4nrYX-iTXA3Tyk)RftNU703(h+qUZN4Dv7O(D0g",
          "phase_state": "z",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 13,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 15,
        "transition_admitted": true,
        "transition_root_hash72": "X4k3co2WSyDk1oy6r(Qi*Ous!R8U/rhup1Yn921)y<AiA3eX*dCTY)qgPW2pJlLLNe18tTOo",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:66"
          ],
          "cell_id": "cell:66",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 15,
          "correction_applied": {
            "denominator": 1,
            "numerator": 2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")WhsH1ZrjMI)Ic!1e3VSUnPu-LO5jNHmjLW5Ai0PJjO?MOY9zCJaQtI*dTjX4yLMQRT?(t7t",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "proposed_energy": 13,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:67",
      "cell_identity_count": 1,
      "cell_root_hash72": "T*vGmfge*rdy9*PwdLK282Wu3wcP-NMX4PzmRaSAcTUf9WGAe-R/02UC!npu5Q5y9>dg6uZf",
      "column": 4,
      "domain_id": "INFORMATION_ENERGY",
      "energy_credit": 25,
      "global_index": 67,
      "lane_count": 3,
      "lo_shu_value": 5,
      "phase_tensor": "w",
      "proposed_energy_credit": 25,
      "row": 7,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:7",
      "transition": {
        "admitted_energy": 25,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:67",
        "current_phase": "w",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "xy",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:67",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKlvc5<7ji5wSCe(l<LJ1RXP(>tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 25,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 25,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:67",
          "constructive_proposal": true,
          "lane_root_hash72": "YaXw6j+JAaaKs6pwfMnx/0I+rOF4*pSVv?rwQ*<BanDD<zA<t(n4c!J!kvvSIo7Z4R1wrxcD",
          "phase_state": "w",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 25,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 25,
        "transition_admitted": true,
        "transition_root_hash72": "4C9irckoIyzopSfXhRFLt0K(FecMnFI+psMQllYvH0zjlRkDXR!n73N2H0hE93gV5Smgt((Q",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:67",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 25,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zV0dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*AfUvRgVFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 25,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:68",
      "cell_identity_count": 1,
      "cell_root_hash72": "aM/<ual8o/hZ1J?6U/hw<wOJ3uml2unkj>pagnh0CU6b!l75Me*Z4x/9Syzytgcy)cs5rVfg",
      "column": 5,
      "domain_id": "INFORMATION_ENERGY",
      "energy_credit": 35,
      "global_index": 68,
      "lane_count": 3,
      "lo_shu_value": 7,
      "phase_tensor": "x",
      "proposed_energy_credit": 37,
      "row": 7,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:7",
      "transition": {
        "admitted_energy": 35,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:68",
        "current_phase": "xy",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "yx",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:68",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bScbqpYhZ7VQWsg4/NqX>2QuGWU(0JlfI>UD/vTL>827yUjN!SRCg7qQc5Mo90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 37,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 35,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:68",
          "constructive_proposal": true,
          "lane_root_hash72": "vlenQs+cKDusmgg8cMwqrylTWd)mBz5La/Ki/7QYEcbwvE0y3-QiRY0?WFHAL7uV+FrL3IWg",
          "phase_state": "xy",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 37,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 35,
        "transition_admitted": true,
        "transition_root_hash72": "Hm8unPT+6rq!>B84nub>amYMR41ct)FMuoDWGQI/HikEEOF!uj!+LP8aS34*Wd(Z!zuJeXay",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:68"
          ],
          "cell_id": "cell:68",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 35,
          "correction_applied": {
            "denominator": 1,
            "numerator": -2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G6>xJ6VH!Yjtu5QR+XZ3rMzy5GG/sQUb03FcOUwo>eswrvjjqtBiTvuc/84-KbvF-iuRTWm9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "proposed_energy": 37,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:69",
      "cell_identity_count": 1,
      "cell_root_hash72": "Rof7H1G/57EjHICHil<zasgDTHak)JnfBpMUn<4(<pBozE1UORCz!<>w2?e1pwJBa04YfOvl",
      "column": 6,
      "domain_id": "INFORMATION_ENERGY",
      "energy_credit": 20,
      "global_index": 69,
      "lane_count": 3,
      "lo_shu_value": 4,
      "phase_tensor": "y",
      "proposed_energy_credit": 21,
      "row": 7,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:7",
      "transition": {
        "admitted_energy": 20,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:69",
        "current_phase": "yx",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "zw",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:69",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU(0KkfI>UD/vTL>827xQoN!SRCg7qQc4Hu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 21,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 20,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:69",
          "constructive_proposal": true,
          "lane_root_hash72": "OEWThbCnQKiQ/Bqw/u*U9tH<UTv*PBnxSNnUGoMbJBHj6Sll<(B9ot(b(lL0KrR>NfG>9ipT",
          "phase_state": "yx",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 21,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 20,
        "transition_admitted": true,
        "transition_root_hash72": "tlj!Fhm5PgAQhL>rGRMc(gjJcx*g0CBwmNg!35EYg-pUc+nEjxFi1gF2093DmjB2VMUnzdBr",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:69"
          ],
          "cell_id": "cell:69",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 20,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G5/CI7VH!Yjtu5QR+XZ3rMzy5FB?sQUb03FcOUwo>eswrvjjrsBiTvub(84-KbvF-iuRTXl9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 21,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:70",
      "cell_identity_count": 1,
      "cell_root_hash72": "cTzQp?1eE)7IeN!6Ui/p(rRek/y6x/37oLOcim+KRbmgD7-DAo4SvOehoWOTCQyc0CzAPrpx",
      "column": 7,
      "domain_id": "INFORMATION_ENERGY",
      "energy_credit": 45,
      "global_index": 70,
      "lane_count": 3,
      "lo_shu_value": 9,
      "phase_tensor": "z",
      "proposed_energy_credit": 45,
      "row": 7,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:7",
      "transition": {
        "admitted_energy": 45,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:70",
        "current_phase": "zw",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "wz",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:70",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKmnj5<7ji5yQCe(l<LJ1RXP<)tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 45,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 45,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:70",
          "constructive_proposal": true,
          "lane_root_hash72": "G*WUcw+r-JtH/3oULm6kf*QbG<6d6C-x(!c!?Mv8fj+Ud!J3Y+gsfuEG+zHwR4S8qV!OQ7N/",
          "phase_state": "zw",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 45,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 45,
        "transition_admitted": true,
        "transition_root_hash72": "G*TU*XH0Bq46mCyJ7yG1bBU/dHCVal+tg!9<>UyH(Rz5nNhPS-89pAa+>gKn)RZDA6uJvr8S",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:70",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 45,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zX!dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*B7+vRiTFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 45,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:71",
      "cell_identity_count": 1,
      "cell_root_hash72": "tLP2dSTOUj7xa?1/+eZ2<j7>5SrVTmrshMsoT99grBkDJD)4TZXT8QVR9hXsNRYQN9dv+z!G",
      "column": 8,
      "domain_id": "INFORMATION_ENERGY",
      "energy_credit": 10,
      "global_index": 71,
      "lane_count": 3,
      "lo_shu_value": 2,
      "phase_tensor": "w",
      "proposed_energy_credit": 9,
      "row": 7,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:7",
      "transition": {
        "admitted_energy": 10,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:71",
        "current_phase": "wz",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "x",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:71",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "+c6!S2t8XiE/VvfLaJRX)If8-UTHB(j7gXU>yB02Mta3Dr-FDQrik2qcxRBxDJq-d!ff*rZN",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 9,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 10,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:71",
          "constructive_proposal": true,
          "lane_root_hash72": "/IT0z/PMTnwQKYGa?V9ktdY3)>7+LhjsKw721NueyKrXNbKjZD)mGWvfWZV09/fDbmkIyEH5",
          "phase_state": "wz",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 9,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 10,
        "transition_admitted": true,
        "transition_root_hash72": "(QPVimx8XBPCUw(PEJ+A>JNWNP!AZD6?0gZNF?f<ZHYJKkW1z!8>*IYeFkR(2S4s5h0bP?cd",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:71"
          ],
          "cell_id": "cell:71",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 10,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "9zZVuHr1)RL72NV>c5SMCp*Ej2jp+yoTsuwMWbMu2?5912N8UctIXbD4gt-flYKoTTqQ4DC7",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 9,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:72",
      "cell_identity_count": 1,
      "cell_root_hash72": "eKzL0S>nUpbSlkfne27CnbQ(PqYu)>ErY-(*baGq<OCBz4Gejx4grK+Dvr89f7smYl(BgDe4",
      "column": 0,
      "domain_id": "CANONICAL_REVALIDATION",
      "energy_credit": 40,
      "global_index": 72,
      "lane_count": 3,
      "lo_shu_value": 8,
      "phase_tensor": "x",
      "proposed_energy_credit": 41,
      "row": 8,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:8",
      "transition": {
        "admitted_energy": 40,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:72",
        "current_phase": "x",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "y",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:72",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU(1CrfI>UD/vTL>827zOoN!SRCg7qQc6Fu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 41,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 40,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:72",
          "constructive_proposal": true,
          "lane_root_hash72": "BFaNFvrAQ8WmUQnJ6?tvexoSHC0(ab1l*CHndcGHM7clpZPaQPjfeDt!0h)lPEuFnY41vMn5",
          "phase_state": "x",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 41,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 40,
        "transition_admitted": true,
        "transition_root_hash72": "MqIa9mw5*)SHElv>Q1CAY4Yi/iVW!hpGrD-jOV8-TW>wKgeyEIYKTW/1I?ZK89xt(cxUuZWE",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:72"
          ],
          "cell_id": "cell:72",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 40,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G7+CI7VH!Yjtu5QR+XZ3rMzy5Hz?sQUb03FcOUwo>eswrvjkjzBiTvub(84-KbvF-iuRUPs9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 41,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:73",
      "cell_identity_count": 1,
      "cell_root_hash72": "<O3cIY-RHrwT6B8<?cg*(GfT<dyFwm4GA</ttp)06PWM2k4vmldnGKQxCsbwyDyro!pAwEYK",
      "column": 1,
      "domain_id": "CANONICAL_REVALIDATION",
      "energy_credit": 5,
      "global_index": 73,
      "lane_count": 3,
      "lo_shu_value": 1,
      "phase_tensor": "y",
      "proposed_energy_credit": 5,
      "row": 8,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:8",
      "transition": {
        "admitted_energy": 5,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:73",
        "current_phase": "y",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "z",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:73",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "l6Mnaw8gg4A5SI/9YFbvqzEn!Dkcb7Cyt!rIAWVMvFVmLy)YJJR3I!35acXqMy76JV2!It6u",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 5,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 5,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:73",
          "constructive_proposal": true,
          "lane_root_hash72": "UdGeo6CGX<a/5-LqYvXd9TBQd2G8ctX/Mf9?x6/M1D?<DaC3UAaWTxF6Qlvk!/Fr>3q75f-o",
          "phase_state": "y",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 5,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 5,
        "transition_admitted": true,
        "transition_root_hash72": "yJfZBOeYZ!Slf/3aJLNNBw-xwL62jl7!PBLV/N9mi7FZpLM)2k9gAnPKb)cvC?PlSlJPiS2i",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:73",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 5,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "DW1i*Y1i9k1>-hVz(qM!Ip6*f-t6g*P-Eq7D0NQo3b2B6VCAazqaFlT55GsQ>0LZCT>HI7Wh",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 5,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:74",
      "cell_identity_count": 1,
      "cell_root_hash72": "FzrLqIdVp-3bI>8zUbDeJqaxos)uYrTb6(q<YXka6q6xqGDyt)dj4Id-<c!0z/s71s0uND65",
      "column": 2,
      "domain_id": "CANONICAL_REVALIDATION",
      "energy_credit": 30,
      "global_index": 74,
      "lane_count": 3,
      "lo_shu_value": 6,
      "phase_tensor": "z",
      "proposed_energy_credit": 29,
      "row": 8,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:8",
      "transition": {
        "admitted_energy": 30,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:74",
        "current_phase": "z",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "w",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:74",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwK0xRsaA4kpW<5srpQ>FOa?JkSjl/nmpoIa38-JLYraYn2xRx!w96x?fvDh)g?571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 29,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 30,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:74",
          "constructive_proposal": true,
          "lane_root_hash72": "8dH9JvGQW71/HY?8QJnjI*QCqN+zd<X5>4nrYX-iTXA3Tyk)RftNU703(h+qVWP4Dv7O(D0g",
          "phase_state": "z",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 29,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 30,
        "transition_admitted": true,
        "transition_root_hash72": "V4kHGy(WSyCq<nz6r(Re>Muu/PgP<qbLd3Zr<e<)y)BiA3eX/hHJY<umER7pLePzVj18sVKt",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:74"
          ],
          "cell_id": "cell:74",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 30,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")YaxG2ZrjMI)Ic!1e3VSUnPu-MT?jNHmjLW5Ai0PJjO?MOYawEJaQtH/dTjX4yLMQRT?)q9t",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 29,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:75",
      "cell_identity_count": 1,
      "cell_root_hash72": "(4X4tpFB!-xIZQ5XL-j)?MfXZWasVty2f3L4??<Fv!lndXZ/qcjCon-cCn5Bq0iGOezRS-73",
      "column": 3,
      "domain_id": "CANONICAL_REVALIDATION",
      "energy_credit": 15,
      "global_index": 75,
      "lane_count": 3,
      "lo_shu_value": 3,
      "phase_tensor": "w",
      "proposed_energy_credit": 13,
      "row": 8,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:8",
      "transition": {
        "admitted_energy": 15,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:75",
        "current_phase": "w",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "xy",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:75",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "6EwL?xRsaA4kpW<5srpQ>FOa?JkSjl/nnooIa38-JLYraYn2vYs!w96x?fvDh(b5571qpnGn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 13,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 15,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:75",
          "constructive_proposal": true,
          "lane_root_hash72": "YaXw6j+JAaaKs6pwfMnx/0I+rOF4*pSVv?rwQ*<BanDD<zA<t(n4c!J!kvvSJl9Z4R1wrxcD",
          "phase_state": "w",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 13,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 15,
        "transition_admitted": true,
        "transition_root_hash72": "xVrTF5W6ruQp4H9I-sY2-bN8As/mMT<!O<ZmULMD7Thsq2IdWyb?n3vAzfba+W3RR<<3vIpc",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:75"
          ],
          "cell_id": "cell:75",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 15,
          "correction_applied": {
            "denominator": 1,
            "numerator": 2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": ")WhsH1ZrjMI)Ic!1e3VSUnPu-LO5jNHmjLW5Ai0PJjO?MOYaxDJaQtI*dTjX4yLMQRT?)r8t",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "proposed_energy": 13,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:76",
      "cell_identity_count": 1,
      "cell_root_hash72": "j<G7?ApBRQZ/A7QjwhKlmdxC!+JPJ3zYYtk?t3u6Yv6GX(RwF0aszg5h>ewmp0P?t-WE3jXJ",
      "column": 4,
      "domain_id": "CANONICAL_REVALIDATION",
      "energy_credit": 25,
      "global_index": 76,
      "lane_count": 3,
      "lo_shu_value": 5,
      "phase_tensor": "x",
      "proposed_energy_credit": 25,
      "row": 8,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:8",
      "transition": {
        "admitted_energy": 25,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:76",
        "current_phase": "xy",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "yx",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:76",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKmtd5<7ji5wSCe(l<LJ1RXP(>tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 25,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 25,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:76",
          "constructive_proposal": true,
          "lane_root_hash72": "vlenQs+cKDusmgg8cMwqrylTWd)mBz5La/Ki/7QYEcbwvE0y3-QiRY0?WFHAM4wV+FrL3IWg",
          "phase_state": "xy",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 25,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 25,
        "transition_admitted": true,
        "transition_root_hash72": "F50uXLxOGSpQ4DqAEENcbMIp5VNIgVOnzUdl)Pqr7Gq9r0>clH2-Wrnc8?8(e>BV!)YEYCKw",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:76",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 25,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zV0dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*BdVvRgVFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 25,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:77",
      "cell_identity_count": 1,
      "cell_root_hash72": "?!0s?r+4Bfdfxcud-/4Mt2n/Wrv)LAkFbGljc+0aj4noddOSppzVc1hb*wCQmOWb7qY0IH1A",
      "column": 5,
      "domain_id": "CANONICAL_REVALIDATION",
      "energy_credit": 35,
      "global_index": 77,
      "lane_count": 3,
      "lo_shu_value": 7,
      "phase_tensor": "y",
      "proposed_energy_credit": 37,
      "row": 8,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:8",
      "transition": {
        "admitted_energy": 35,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:77",
        "current_phase": "yx",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "zw",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:77",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -2
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bScbqpYhZ7VQWsg4/NqX>2QuGWU(1HmfI>UD/vTL>827yUjN!SRCg7qQc5Mo90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 37,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 35,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:77",
          "constructive_proposal": true,
          "lane_root_hash72": "OEWThbCnQKiQ/Bqw/u*U9tH<UTv*PBnxSNnUGoMbJBHj6Sll<(B9ot(b(lL0LoT>NfG>9ipT",
          "phase_state": "yx",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "l</MsQT-GA(*F3qOl<9W1W>OzbghE>)4NyV4Qb2wZ9DCPLmMm(oj9gEI<>vZjm2>mFLQjjb<",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 37,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 35,
        "transition_admitted": true,
        "transition_root_hash72": "xjj!Fis)UeAQhL!yyRMd-lhJcy!60Iwyo<Mj6?FYg-pUd-nEkBuo1gF22iKVmjC6SOQnzdCo",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:77"
          ],
          "cell_id": "cell:77",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 35,
          "correction_applied": {
            "denominator": 1,
            "numerator": -2
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G6>xJ6VH!Yjtu5QR+XZ3rMzy5GG/sQUb03FcOUwo>eswrvjkouBiTvuc/84-KbvF-iuRUUn9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 2
          },
          "proposed_energy": 37,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:78",
      "cell_identity_count": 1,
      "cell_root_hash72": "XyOx/JUWy1drEdl*hRGBNhI8l>nm6+1Cj26LLhNT*TKzIpfIvW4mSaES?UVmDkJHD+drD11i",
      "column": 6,
      "domain_id": "CANONICAL_REVALIDATION",
      "energy_credit": 20,
      "global_index": 78,
      "lane_count": 3,
      "lo_shu_value": 4,
      "phase_tensor": "z",
      "proposed_energy_credit": 21,
      "row": 8,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:8",
      "transition": {
        "admitted_energy": 20,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:78",
        "current_phase": "zw",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "wz",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:78",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "gradient_state": "EXPANSION_PRESSURE",
          "lane_root_hash72": "sf?bRdbqpYhZ7VQWsg4/NqX>2QuGWU(1IlfI>UD/vTL>827xQoN!SRCg7qQc4Hu90oDLKIBn",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 21,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 20,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:78",
          "constructive_proposal": true,
          "lane_root_hash72": "G*WUcw+r-JtH/3oULm6kf*QbG<6d6C-x(!c!?Mv8fj+Ud!J3Y+gsfuEG+zHwRcK8qV!OQ7N/",
          "phase_state": "zw",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": ">dsc/R7FtK9K7ZHksVJ!qnR)PXcWtxL9o?GbOj2G*RXlJJuT71xQfd0tuSIPi3zKaO(vnnra",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 21,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 20,
        "transition_admitted": true,
        "transition_root_hash72": "AxPjV!SS-qtD7V6DaUt34CrGK-?5HzSsfq1)Q5b7jy1JL/w9yj?A+gLrWf<VJ*Q4B*ftCFNf",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:78"
          ],
          "cell_id": "cell:78",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 20,
          "correction_applied": {
            "denominator": 1,
            "numerator": -1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "G5/CI7VH!Yjtu5QR+XZ3rMzy5FB?sQUb03FcOUwo>eswrvjkptBiTvub(84-KbvF-iuRUVm9",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "proposed_energy": 21,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:79",
      "cell_identity_count": 1,
      "cell_root_hash72": "8xEHH/vXb7tl4dApjDh5qkEmnj116fvWxdlkS(+*(HDo9hQ/q<kgDZ7d*1N?ffATS/p9c4cA",
      "column": 7,
      "domain_id": "CANONICAL_REVALIDATION",
      "energy_credit": 45,
      "global_index": 79,
      "lane_count": 3,
      "lo_shu_value": 9,
      "phase_tensor": "w",
      "proposed_energy_credit": 45,
      "row": 8,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:8",
      "transition": {
        "admitted_energy": 45,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:79",
        "current_phase": "wz",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "x",
        "nontrivial_dynamic_closure": false,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:79",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "gradient_state": "EQUILIBRIUM",
          "lane_root_hash72": "JMIQp3+cile>WKCIAuo<VZaZtWqeHRKmwa5<7ji5yQCe(l<LJ1RXP<)tWsM9VwNj61f/(nHu",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": false,
          "proposed_energy": 45,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 45,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:79",
          "constructive_proposal": true,
          "lane_root_hash72": "/IT0z/PMTnwQKYGa?V9ktdY3)>7+LhjsKw721NueyKrXNbKjZD)mGWvfWZV0917DbmkIyEH5",
          "phase_state": "wz",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "R4H3IrjLV0BaN9(3nKZMLvUF3cBr!DQcg1ocJ)PQy!>+EZ6GuxdvUmQ(tRVrKUm?Vv0i6yiz",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 45,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 45,
        "transition_admitted": true,
        "transition_root_hash72": "F96O!>JVG0Lbz>x-kDcPrs2(V9TCGeqe?vD6p>n5Rg!iWV5PMh2va+oL0uPtoykuH4Lg*+vN",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [],
          "cell_id": "cell:79",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 45,
          "correction_applied": {
            "denominator": 1,
            "numerator": 0
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "UxfYV*mXTLbPR8zX!dlrPL>S?IQ)w>rKWa6mId3s1GrtoKHI</pyOzN!Cy*BgSvRiTFQa(+D",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": 0
          },
          "proposed_energy": 45,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_closed": true,
      "cell_id": "cell:80",
      "cell_identity_count": 1,
      "cell_root_hash72": "dibjUmvR2DnF6VdJbg00F/whMnYk9n?j?T<ZvjE?8gN9H4oCXy-T0VwFW*Q8xhdHAhj?65Ox",
      "column": 8,
      "domain_id": "CANONICAL_REVALIDATION",
      "energy_credit": 10,
      "global_index": 80,
      "lane_count": 3,
      "lo_shu_value": 2,
      "phase_tensor": "x",
      "proposed_energy_credit": 9,
      "row": 8,
      "schema": "HHS_TRINARY_PHASE_QUDIT_CELL_V1",
      "subgrid_id": "subgrid:8",
      "transition": {
        "admitted_energy": 10,
        "all_three_lane_witnesses_present": true,
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_id": "cell:80",
        "current_phase": "x",
        "execution_order": [
          "POSITIVE",
          "PLASTIC",
          "ZERO_SUM"
        ],
        "next_phase": "y",
        "nontrivial_dynamic_closure": true,
        "plastic_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cell_id": "cell:80",
          "continuation_admitted": true,
          "creates_information_energy": false,
          "gradient_residue": {
            "denominator": 1,
            "numerator": 1
          },
          "gradient_state": "CONTRACTION_PRESSURE",
          "lane_root_hash72": "+c6!S2t8XiE/VvfLaJRX)If8-UTHB(j8eYU>yB02Mta3Dr-FDQrik2qcxRBxDJq-d!ff*rZN",
          "minimal_polynomial": "rho^3-rho-1",
          "nonzero_gradient_exercised": true,
          "proposed_energy": 9,
          "schema": "HHS_PLASTIC_GRADIENT_LANE_V1",
          "source_energy": 10,
          "trit": 0,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "positive_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "authority_rank_implied": false,
          "cell_id": "cell:80",
          "constructive_proposal": true,
          "lane_root_hash72": "BFaNFvrAQ8WmUQnJ6?tvexoSHC0(ab1l*CHndcGHM7clpZPaQPjfeDt!0h)lQBwFnY41vMn5",
          "phase_state": "x",
          "schema": "HHS_ORIENTED_PHASE_LANE_V1",
          "source_phase_root_hash72": "w!t7bqo/q0xlsmjDpIcX8RyV5AG5B/pMXmD<2diSRY?O-f9Z>)E+8N?U(TV?9w>hsjbelzFx",
          "trit": 1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
        },
        "proposed_energy": 9,
        "schema": "HHS_THREE_LANE_PHASE_TRANSITION_V1",
        "source_energy": 10,
        "transition_admitted": true,
        "transition_root_hash72": "Q7*/u4b9FJgVD0Y0tK6)mg+uStidj0nZ(nUj(XeBitcJiP<D!0vQZCPOK-EiRWr5rH-Wcck8",
        "trinary_is_functional_not_authority_rank": true,
        "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
        "zero_sum_lane": {
          "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
          "cancellation_scope": [
            "cell:80"
          ],
          "cell_id": "cell:80",
          "closure_state": "CLOSED",
          "continuation_admitted": true,
          "corrected_energy": 10,
          "correction_applied": {
            "denominator": 1,
            "numerator": 1
          },
          "global_rejection_propagated": false,
          "lane_root_hash72": "9zZVuHr1)RL72NV>c5SMCp*Ej2jp+yoTsuwMWbMu2?5912N9SdtIXbD4gt-flYKoTTqQ5BD7",
          "pre_correction_residue": {
            "denominator": 1,
            "numerator": -1
          },
          "proposed_energy": 9,
          "schema": "HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1",
          "source_phase_erased": false,
          "trit": -1,
          "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1",
          "zero_sum_residue": {
            "denominator": 1,
            "numerator": 0
          }
        }
      },
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    }
  ],
  "domain_count": 9,
  "expected_total_energy": 2025,
  "global_closure": true,
  "global_rejection_propagated": false,
  "hash72_lattice_block": {
    "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
    "lattice_block_root_hash72": "4wIilTYf3qhD(gDTlAERJ<zuFZUD/BH7GyRsp<WL3QmiTimsBpE*VKSDD2-cZdl2QrSt5S*J",
    "previous_root_hash72": "B(h3Ef)J>*2<*?OY4KKrp7usfVYx/di0+1ZWyQwck*ALp2H3Z2wzV*K(CXYhlyLUSBOm-om5",
    "schema": "HHS_HASH72_TRINARY_LATTICE_BLOCK_V1",
    "sha256_labeled_hash72": false,
    "subgrid_roots_hash72": [
      "f>uI0W16lXeVBjZ26aff(qsLt5(4L--Yvdi*u*FwLB2uI*HA)HsK+n-592B(WI5W!q5>V)F4",
      "?QyhIT?R*gwlD7bAlFtoN9kEwrWC**w5nb)v2iSm*Aw<l36TRgl(K0JGGIQN*>Wa-0yB1rtA",
      "OvFO37?pGRM38BXnfP1zjh)!7Cf)g7T-G3YXEqslZ1Lw?3DnDCVzqbFMJvCZDjcWcV+m!y4b",
      "2XCkynj)u>!z5VS>5x?L2xMY6W3rJPAqo6BBL!TctQ/mxO53?>?0bGzdtbxtqIk!wa(+ajNk",
      "An+7l!9uHgPhtT/v+k2gD3CDayRH-wef>fzuMu4XyH5iTY>p42A5!L9(Q!1G0wY7hCQkR5<I",
      "fGx2WZZ9AS(0j44+JZyslyy/knwZFoCGjD(a!5F38CP4xhGxWT8JI8plm/o6rt0nRwnx2)s>",
      "s/sHh2R(mX)jhc(KAaN(*FEwcE5G+Z+xX/(5baE>tm1Z5d-VSQnoa!wtDeOqiL/v8cs44+M?",
      "fauVSv48jTpQ3Ol4fUy9fQIJYW7w-vRv(H?>Li*u4zIk-ewD(4H*P>/(G!6H>JdlIE?sJcP8",
      "?JK(Mt5dSbX+/!v7j72PvibewY(h7/GZEQDEXKAAbFyaTEKwBwX6Ne!<w39>pPauei7*KMWG"
    ],
    "u72_router_root_hash72": "/R0jUD5B4mJCII/u<nsN0bMocN/gahJe4I47zMbRT5pPQrz?cp!AG/!(sTwCvxy1TbeMq9)8",
    "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
  },
  "hierarchical_reconstruction": {
    "admitted_lattice_block_root_hash72": "4wIilTYf3qhD(gDTlAERJ<zuFZUD/BH7GyRsp<WL3QmiTimsBpE*VKSDD2-cZdl2QrSt5S*J",
    "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
    "hierarchical_reconstruction_verified": true,
    "lattice_block_matches": true,
    "reconstructed_lattice_block_root_hash72": "4wIilTYf3qhD(gDTlAERJ<zuFZUD/BH7GyRsp<WL3QmiTimsBpE*VKSDD2-cZdl2QrSt5S*J",
    "reconstruction_root_hash72": "/mijonKZhbQ8QJ-IjYy-/oVrWN>>TH5Xs/vu<3ANcyYY!aP<b9DHgY9VJp)opZ1v5*/m<t3u",
    "router_matches": true,
    "schema": "HHS_EXECUTABLE_HIERARCHICAL_RECONSTRUCTION_V1",
    "subgrids_match": true,
    "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
  },
  "lane_identity_is_not_cell_identity": true,
  "lane_projection_count": 243,
  "lattice_root_hash72": "s9q6ZCI!lm2Lx1zIdgquSd9rMuRC!GUJaLmB+)zFR4Dqy0rlR?!1A7)8LCa2wk67<//ghu+(",
  "pass067_1_root_hash72": "B(h3Ef)J>*2<*?OY4KKrp7usfVYx/di0+1ZWyQwck*ALp2H3Z2wzV*K(CXYhlyLUSBOm-om5",
  "rejection_codes": [
    "REJECT_POSITIVE_LANE_BYPASSES_PLASTIC_EQUILIBRIUM",
    "REJECT_PLASTIC_GRADIENT_BYPASSES_ZERO_SUM_CLOSURE",
    "REJECT_ZERO_SUM_CORRECTION_ERASES_SOURCE_PHASE",
    "REJECT_LANE_ACQUIRES_COMPLETE_CELL_IDENTITY",
    "REJECT_TRINARY_VALUE_IMPLIES_AUTHORITY_RANK",
    "REJECT_PHASE_TRANSITION_WITHOUT_ALL_THREE_LANE_WITNESSES",
    "REJECT_PLASTIC_GRADIENT_CREATES_INFORMATION_ENERGY",
    "REJECT_NEGATIVE_LANE_PROPAGATES_GLOBAL_REJECTION",
    "REJECT_CELL_CLOSES_WHILE_SUBGRID_IMBALANCED",
    "REJECT_GLOBAL_LATTICE_WITH_UNRESOLVED_LOCAL_RESIDUE"
  ],
  "schema": "HHS_81_CELL_TRINARY_QUDIT_LATTICE_V1",
  "subgrid_count": 9,
  "subgrids": [
    {
      "all_cells_closed": true,
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_ids": [
        "cell:00",
        "cell:01",
        "cell:02",
        "cell:03",
        "cell:04",
        "cell:05",
        "cell:06",
        "cell:07",
        "cell:08"
      ],
      "cell_roots_hash72": [
        "p2h0ISB4X70<*I>sBTI/geDUhdk*S/9xCo4+W4JGs0jBHV-)RmdgZk))8MdWll87-TXgmErm",
        "rXY(esTxaTy2WYUJhAN/2!BB8MT)sPs(Qt7M4C-(?3sQHJV2SpAzQo9+<hRkh1QZ/tpLyv2T",
        "Y(RVMz0B!2vzF7y1D?p?Jrn90>scDMymCVDxM!+1J<AS<5fwCc4AuBlDfS6jRT/PPHYGjBrD",
        "qTe2CH*UNU>gi5)R?evM-5cigdkOQzAnp467dAkoL9HrwOA2NjFrZKOkwhto4U5QlaqC00BO",
        "SQzN/ODP39FuclCT4yGWo90UL)3X5IcboJ1xOf+dO0xJdYn+CKqqZvPyNEgJxALc7/sioDCs",
        "c2VK!<pvp7!Dh*1uXi1A?+PeT(n3U>ra7(MPh-6og9-m!fjFUQUnDC*4pDKeVOC*8iKm?k4h",
        "!2>R?X40VI2Xwdg/IFT(qIMmfPPCLTc>WhXRW0Y/z*r*7l-/8?qE9ppzgC19fOkQJ?3IxdWe",
        "7k+Nw6)SoLsrQpBP9780A5+Fjq3HlfyLGaTT1eo!Kal3OOFsr+3g4gCUQ7VSiZC(ZJaMFV?R",
        "*r!F<XRjYBfYZ8kpyUQOIZ28ftss*HIyh6KhzFvDcQYaRt-mi3j<s/rB4Pu?Hjz6Bpy*lC<G"
      ],
      "cluster_energy": 225,
      "columns": [
        75,
        75,
        75
      ],
      "diagonals": [
        75,
        75
      ],
      "domain_id": "FORMAL_ALGEBRA",
      "local_lo_shu_conservation": true,
      "rows": [
        75,
        75,
        75
      ],
      "schema": "HHS_LO_SHU_TRINARY_SUBGRID_V1",
      "subgrid_id": "subgrid:0",
      "subgrid_root_hash72": "f>uI0W16lXeVBjZ26aff(qsLt5(4L--Yvdi*u*FwLB2uI*HA)HsK+n-592B(WI5W!q5>V)F4",
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "all_cells_closed": true,
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_ids": [
        "cell:09",
        "cell:10",
        "cell:11",
        "cell:12",
        "cell:13",
        "cell:14",
        "cell:15",
        "cell:16",
        "cell:17"
      ],
      "cell_roots_hash72": [
        "htXf!5W0dP7eEOfK<6Jq?X4*7IFjPj9Wu88yuZ/QPWQoMPqjtocv?yiKPGMEmF>GkuDkM(tn",
        ">Mc?Abfubpo*Bd<4L(Djyz*MQ8wnUb?uGTc97gWze3U?OYv2CRBy65QmkQ6x5Jqo?aLh+<j1",
        "A0jsGJzS<ueKNy*4!R-kx*OsRF4?-RoSI0roLnkfb?dmRSImkkGRgFUzm>RtG)hHlUGle?i<",
        "L63?4tR+e2uXUlf?CWBjY3No1B<LQW4aVP8>bpkaysmziQvenN9gGHSOAQ?tnURLm/jsH7vW",
        "Op148qc*5IS2O8cMS?-BIc5QLwbpE9e5o2BE*5fJkAL8?8pu/ly-eIslZkdiNM-ZnDw1NN71",
        "6+ct8aQ+jGdsjnYtJ1?iUN)YUJ)8lfOr(sjwzB*J5iaDeU!Lgwpos0C2FoIX1KflC2LC!J/a",
        "EnA(NCMMu*nzfeZyCJSxIC8IfPA8iK67P>oiSEktUosjmdLA?>srkDCQgV8w7lLPoRIkcRgO",
        "A2F*)>MHlL2*9GyAN9dUieW7z!cFMS4C-4CQwKJfryZb<8D!3gYMY7+7FQxKuxf(Fmx6LRT*",
        "/94Yo-6PxQX(>rmoANRXTnq-p76b*D<3--QI1h!T1yjXANcIW<pJL8rxfWIZXtd<B*QBQH9k"
      ],
      "cluster_energy": 225,
      "columns": [
        75,
        75,
        75
      ],
      "diagonals": [
        75,
        75
      ],
      "domain_id": "SYMBOLIC_LOGIC",
      "local_lo_shu_conservation": true,
      "rows": [
        75,
        75,
        75
      ],
      "schema": "HHS_LO_SHU_TRINARY_SUBGRID_V1",
      "subgrid_id": "subgrid:1",
      "subgrid_root_hash72": "?QyhIT?R*gwlD7bAlFtoN9kEwrWC**w5nb)v2iSm*Aw<l36TRgl(K0JGGIQN*>Wa-0yB1rtA",
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "all_cells_closed": true,
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_ids": [
        "cell:18",
        "cell:19",
        "cell:20",
        "cell:21",
        "cell:22",
        "cell:23",
        "cell:24",
        "cell:25",
        "cell:26"
      ],
      "cell_roots_hash72": [
        "gtc9(cN6szCzXi58AZbp!XXsIUIbnpacPll1o8ql6qh<HzcBFxn+3juyS4Zts+eS/JS1/c(r",
        "/-EIp)8t09mgRmADca+Dx8lbCd*KYeEaAq(x)ZAu6sF4/YbNK<+x(S(CXhzFx2dBwtJ4zX<b",
        "pD>/SWAY5Y+kmgcIgjN7kze4V2/YifnELgugZwtV4SBOukkcbPZ<ai7g2)X(X329svnjSZ/P",
        "F70YKKloZzq4>SO068oGMAvRvaV1lY(1>r(x*o/Pf6y6K)W4wB64uUXg5sKg5>uO+KA?oMRg",
        "FE-ngtLNOEKUi<VwQyLEPCE46cBD>XK(ge3ERc>Ug/f5SLeKrL>VLeUCpY(xqVxVo!f9jgOS",
        "jYuZnUd4ULNy/)uA71>6O(GQUrVwLVBnUOy+>vwEm1SUxqz!j5sisWWLfH-TPam+fH2)60xB",
        "ErUt(y9>7YpG)Ilq0yW>1y1HMUgF0BtmRC7NLsHMaQXrUVj8>8s3)IzMGwD!/W4tN8m0*QF3",
        "nRMKe4WbCWqM1Ugbzyj/hdS*K0UGB-z6jX6euT>IVh24LkmG6C?O224?GBdbUo/5yUau-l1-",
        "c3XF)qcHqKDPqe<IC+80lMCp4mXxNjdRaj)b+F*aq(Rntnm3?hUa(vpVkXCCd*L3IxQabPy!"
      ],
      "cluster_energy": 225,
      "columns": [
        75,
        75,
        75
      ],
      "diagonals": [
        75,
        75
      ],
      "domain_id": "SEMANTIC_TRANSLATION",
      "local_lo_shu_conservation": true,
      "rows": [
        75,
        75,
        75
      ],
      "schema": "HHS_LO_SHU_TRINARY_SUBGRID_V1",
      "subgrid_id": "subgrid:2",
      "subgrid_root_hash72": "OvFO37?pGRM38BXnfP1zjh)!7Cf)g7T-G3YXEqslZ1Lw?3DnDCVzqbFMJvCZDjcWcV+m!y4b",
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "all_cells_closed": true,
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_ids": [
        "cell:27",
        "cell:28",
        "cell:29",
        "cell:30",
        "cell:31",
        "cell:32",
        "cell:33",
        "cell:34",
        "cell:35"
      ],
      "cell_roots_hash72": [
        "ZA2MoY6VHnw6/*/7vhtQBnQprq<SRkJWA9QiF8nUFk1b3oMra?7z7rv-8?psbwl3dcxlh5oo",
        "JSMqgmwHBrWrod)/Otbx3Gg*KZgmSKoEN!)m/IPzsErTzl*>15OHEyiLo3jsCSk*O6zqIwTp",
        "4!CjF*yh8Sv1rJwAi-w)Sc5?y<CI<vUV)UEEzGB-lnkI7*QS*-xuO?oGBYM7mMQfR?rr5OsQ",
        "MDEd?FlXhTCaRzwwLD9BSiSL62n(k6umOZZZQjEdl)WWKYavuIG57kuh5Xd-3hWJ)TTc4UKM",
        "EDgjXJtoVABcnkQmUai6D/tUVvW/vZ)dgqptzjcyOF-)*9rDJ/SX+T9ytysFm)439-mUDxi(",
        "1)RN7n-?UHrDYHU4/RsBTS-iPyw6SOvdnJGPvCI)7QH5!ZgtgT8B1imxgVe8JHHEGs>DB6hG",
        "ey)x?OHt(y!zed8ag9LRa8Igi6>8?ATSj3KT0XG<dn/!IYSdt+wW+cmLplEtlw>gkxkz+Hwm",
        "3rOOopeT/okuRRBhMNu7(3qP+YbT-ADO16*kFSVQQa?altajUICZrXmX<7NhN0yVmDx(Eh>b",
        "pX5g/)hczO*/LT2q4Ih-X27tWTKA?lKf*l?Vwuqra1(p/w7RSJkpoZmwBpr?5!vcoCf*NZc?"
      ],
      "cluster_energy": 225,
      "columns": [
        75,
        75,
        75
      ],
      "diagonals": [
        75,
        75
      ],
      "domain_id": "RUNTIME_EXECUTION",
      "local_lo_shu_conservation": true,
      "rows": [
        75,
        75,
        75
      ],
      "schema": "HHS_LO_SHU_TRINARY_SUBGRID_V1",
      "subgrid_id": "subgrid:3",
      "subgrid_root_hash72": "2XCkynj)u>!z5VS>5x?L2xMY6W3rJPAqo6BBL!TctQ/mxO53?>?0bGzdtbxtqIk!wa(+ajNk",
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "all_cells_closed": true,
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_ids": [
        "cell:36",
        "cell:37",
        "cell:38",
        "cell:39",
        "cell:40",
        "cell:41",
        "cell:42",
        "cell:43",
        "cell:44"
      ],
      "cell_roots_hash72": [
        "x2XWp8Txe/7kpm(mqB*x>4HB?OvbY3i*11DLyhN<2wow-jy8(78VSANT<XNjdl81k8ja?jN6",
        "95L<<mC1u++lmRW-8iZ>lD*ybs2kMK07IFvv-pmiTYEK8Zb-vuOgQZPfS!muddM54gqyDSDo",
        "fbRDNcnyuC8nM>ZqKEI-Q/xg*9tdrXBmn5d8kxL1XxADG1VZ!0aM41)AGUHSTfZxoBGOJ(XD",
        "r7uKsFSE0TQtYOGusZ4(MF1pQ3lX>w*BOxk>I4L4k1+xDVdq>iqyZTbjYnWv-Q8zQQ*E)HaZ",
        "kRwrOz-Jvq(AwrM72iehaaZ2hsfGWX8lpH9H)732dm4Eh(xMHx*sTkV3YW5C6IpE34hDQYP6",
        "EZ(/C7rILVs+sHY7N!>qgfy+T0mYuu93(BYG(saYhCfFl!shva<OM/bYrXCI/TC14/0)ZlYc",
        "RPNaww+k8ngjfN2L*5zN9E-Myj0!uh5qWYisxuOs?n6ZNwD2vuv3PCj7UIDHaSHdSEbdQgQA",
        "yV/LCbKmdLJWiRg1hFqUd<pLYk6rgOnBFdLgsChsVVG(nhA4V-?uSQ)LXRtS)Cj9<RgSxHwA",
        "IDJGOQ4iuWyo0zp7)eTHWJKpUYSo+R7IM6sFMcP+UcWe-KugYy2mWCmhlmEoIg8st)9!BF5("
      ],
      "cluster_energy": 225,
      "columns": [
        75,
        75,
        75
      ],
      "diagonals": [
        75,
        75
      ],
      "domain_id": "PROVENANCE_AUDIT",
      "local_lo_shu_conservation": true,
      "rows": [
        75,
        75,
        75
      ],
      "schema": "HHS_LO_SHU_TRINARY_SUBGRID_V1",
      "subgrid_id": "subgrid:4",
      "subgrid_root_hash72": "An+7l!9uHgPhtT/v+k2gD3CDayRH-wef>fzuMu4XyH5iTY>p42A5!L9(Q!1G0wY7hCQkR5<I",
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "all_cells_closed": true,
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_ids": [
        "cell:45",
        "cell:46",
        "cell:47",
        "cell:48",
        "cell:49",
        "cell:50",
        "cell:51",
        "cell:52",
        "cell:53"
      ],
      "cell_roots_hash72": [
        "2ZAD+zi1VYa4?2oyC?Zp07e9whH0aqcjDBYv2db?W*Yxf72zx?B4kx8v*TT/-sHceDYv-ir/",
        "SG?c9>9/<U?k5>KD52G5R+enYndY)V47*JX4mbd3qDhv6WjqHP9Y2!DRa3VJx>XHOFn71es*",
        "KKv</m58FnFUK!2Nlon<MJw4Xpriw+m-U7GoiB1Jt3-PMUB7euvA7RkDT>Q2<p9>vzf>g8Ce",
        "p>9+2f(7CM>VDke9(2CBLv6aa*E4Dh7+sCUuqvmIM?e3)yfMFbuw?+wW4?*IvQy2oB+Ro7gO",
        "c9nxhO>cz9hAJ0V/r92i<T4<U>W*XbiBvhGqyG3JVZ28>T*?<*B0Dbx0rN4Czv)Z9H-j84rJ",
        "Soe4gIE*55knGJVX*BRlG<z+dXg)/Nb?GpxdV58Cmk>82Exl8+Sn!v-Vjkq6tXe(F>svH<n<",
        "/BY1aY6VbHccj*(kXt(xznVdGm(QTqke!rKzhCLF-STs9kJer?7xbsm<82bN>Aj99b!Tp?om",
        "wM?bA17(UKeYEO3gNw8NgDRFLx-iv)ullmGny>XxIH6/T<CMR++02yzDgNIgnszg)9*>X1ss",
        "e>QA>rmUt1)g3PvuP*OqcjlDsRFS954SH4R-7hiMqY>sPT!pEMqeUehTb3ZpHno6K6CoT4Z9"
      ],
      "cluster_energy": 225,
      "columns": [
        75,
        75,
        75
      ],
      "diagonals": [
        75,
        75
      ],
      "domain_id": "MULTIMODAL_FUSION",
      "local_lo_shu_conservation": true,
      "rows": [
        75,
        75,
        75
      ],
      "schema": "HHS_LO_SHU_TRINARY_SUBGRID_V1",
      "subgrid_id": "subgrid:5",
      "subgrid_root_hash72": "fGx2WZZ9AS(0j44+JZyslyy/knwZFoCGjD(a!5F38CP4xhGxWT8JI8plm/o6rt0nRwnx2)s>",
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "all_cells_closed": true,
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_ids": [
        "cell:54",
        "cell:55",
        "cell:56",
        "cell:57",
        "cell:58",
        "cell:59",
        "cell:60",
        "cell:61",
        "cell:62"
      ],
      "cell_roots_hash72": [
        "Ygpr(Q43hp(FoQ0n2tf*Jd1W7TGM79EN89J7KSyhFPqd5yJ940DwgLIJEw0k*qjcSaBa<fu)",
        "t9J5VVB3?VhntFgIuJ/fO>lB)y/Ztz0/rq0k7Df<L3PZgBrkmdgTkFsbhMlCYk77)dwH<AqL",
        "Pz82B1glHyKAHN0!bU!UmTqU0KEB8A)ehzRlrgm/z0yo0xmBgeQbj51UytLEJJJ8AeA5RPYN",
        ")MbNL<q!jMSQs-YE(De-wB)T0EYQ!gsoNbwvYvN>Dkk26TBV/i)QX779)t<NF0Zu?t!ZodzF",
        "s<0av<DfoE)jIIcuSL>IQtDB6umvK7ywX6V-11JU)M!)/cr0>9x5myvJnAyUphR4iLD2p7/Y",
        "X6+/6yv9TdgKVmmFW9uFv/dYxu84Hblf/b*-z>dNxGI7N8gq5UKp+7k1wHKP<C2ZUd*Bicc-",
        "FOU+2Uk+<QHn7<A0YrM!wgts0ioc9AEfnwdJYT8?OjdGbp0AyJB6W*In(T/Q(0u7w9ZLn?*i",
        "uZu+LtFC*Eex6m6WapodTHgG>poU>6q8u>SNRZgervvw5??IhlqnYry+)kKc4LoCz1f?!m(w",
        "4-69zQBeeCE+so1e6ZvJAK)eRFe2HTSH-SabMomdx6KRh->0U*BHNo(xzhv-DI)M?w+Kb/h-"
      ],
      "cluster_energy": 225,
      "columns": [
        75,
        75,
        75
      ],
      "diagonals": [
        75,
        75
      ],
      "domain_id": "CONSTRAINT_TOPOLOGY",
      "local_lo_shu_conservation": true,
      "rows": [
        75,
        75,
        75
      ],
      "schema": "HHS_LO_SHU_TRINARY_SUBGRID_V1",
      "subgrid_id": "subgrid:6",
      "subgrid_root_hash72": "s/sHh2R(mX)jhc(KAaN(*FEwcE5G+Z+xX/(5baE>tm1Z5d-VSQnoa!wtDeOqiL/v8cs44+M?",
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "all_cells_closed": true,
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_ids": [
        "cell:63",
        "cell:64",
        "cell:65",
        "cell:66",
        "cell:67",
        "cell:68",
        "cell:69",
        "cell:70",
        "cell:71"
      ],
      "cell_roots_hash72": [
        "K!Ro7oy-JKWCR!etupuA?gahT*9)6THq9(BBMnNiX9vI?1jcpXS4VPnZn82ckg6D*cU4Es/p",
        "hgKVE25H20ZCSwmuYDv*Qr+***P!rTXXu*Yt2<57rmVkBxs((*y66Xp)B*VhrQh4+oPI6dDp",
        "7Nlnlq<dp5G9n+yfhL9T5QxV)0a>Tnww/szcp(vclew)90gTKw1*yOe?cuzgrHYKNq!G(CoV",
        "SJ7m-Zr(b*kHDUaP7h3J?95T2wOZvD>mRJ2MkeaRMJVUPmR)G)7t/(6EvdZ/fu?omfu/w6Z1",
        "T*vGmfge*rdy9*PwdLK282Wu3wcP-NMX4PzmRaSAcTUf9WGAe-R/02UC!npu5Q5y9>dg6uZf",
        "aM/<ual8o/hZ1J?6U/hw<wOJ3uml2unkj>pagnh0CU6b!l75Me*Z4x/9Syzytgcy)cs5rVfg",
        "Rof7H1G/57EjHICHil<zasgDTHak)JnfBpMUn<4(<pBozE1UORCz!<>w2?e1pwJBa04YfOvl",
        "cTzQp?1eE)7IeN!6Ui/p(rRek/y6x/37oLOcim+KRbmgD7-DAo4SvOehoWOTCQyc0CzAPrpx",
        "tLP2dSTOUj7xa?1/+eZ2<j7>5SrVTmrshMsoT99grBkDJD)4TZXT8QVR9hXsNRYQN9dv+z!G"
      ],
      "cluster_energy": 225,
      "columns": [
        75,
        75,
        75
      ],
      "diagonals": [
        75,
        75
      ],
      "domain_id": "INFORMATION_ENERGY",
      "local_lo_shu_conservation": true,
      "rows": [
        75,
        75,
        75
      ],
      "schema": "HHS_LO_SHU_TRINARY_SUBGRID_V1",
      "subgrid_id": "subgrid:7",
      "subgrid_root_hash72": "fauVSv48jTpQ3Ol4fUy9fQIJYW7w-vRv(H?>Li*u4zIk-ewD(4H*P>/(G!6H>JdlIE?sJcP8",
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    },
    {
      "all_cells_closed": true,
      "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
      "cell_ids": [
        "cell:72",
        "cell:73",
        "cell:74",
        "cell:75",
        "cell:76",
        "cell:77",
        "cell:78",
        "cell:79",
        "cell:80"
      ],
      "cell_roots_hash72": [
        "eKzL0S>nUpbSlkfne27CnbQ(PqYu)>ErY-(*baGq<OCBz4Gejx4grK+Dvr89f7smYl(BgDe4",
        "<O3cIY-RHrwT6B8<?cg*(GfT<dyFwm4GA</ttp)06PWM2k4vmldnGKQxCsbwyDyro!pAwEYK",
        "FzrLqIdVp-3bI>8zUbDeJqaxos)uYrTb6(q<YXka6q6xqGDyt)dj4Id-<c!0z/s71s0uND65",
        "(4X4tpFB!-xIZQ5XL-j)?MfXZWasVty2f3L4??<Fv!lndXZ/qcjCon-cCn5Bq0iGOezRS-73",
        "j<G7?ApBRQZ/A7QjwhKlmdxC!+JPJ3zYYtk?t3u6Yv6GX(RwF0aszg5h>ewmp0P?t-WE3jXJ",
        "?!0s?r+4Bfdfxcud-/4Mt2n/Wrv)LAkFbGljc+0aj4noddOSppzVc1hb*wCQmOWb7qY0IH1A",
        "XyOx/JUWy1drEdl*hRGBNhI8l>nm6+1Cj26LLhNT*TKzIpfIvW4mSaES?UVmDkJHD+drD11i",
        "8xEHH/vXb7tl4dApjDh5qkEmnj116fvWxdlkS(+*(HDo9hQ/q<kgDZ7d*1N?ffATS/p9c4cA",
        "dibjUmvR2DnF6VdJbg00F/whMnYk9n?j?T<ZvjE?8gN9H4oCXy-T0VwFW*Q8xhdHAhj?65Ox"
      ],
      "cluster_energy": 225,
      "columns": [
        75,
        75,
        75
      ],
      "diagonals": [
        75,
        75
      ],
      "domain_id": "CANONICAL_REVALIDATION",
      "local_lo_shu_conservation": true,
      "rows": [
        75,
        75,
        75
      ],
      "schema": "HHS_LO_SHU_TRINARY_SUBGRID_V1",
      "subgrid_id": "subgrid:8",
      "subgrid_root_hash72": "?JK(Mt5dSbX+/!v7j72PvibewY(h7/GZEQDEXKAAbFyaTEKwBwX6Ne!<w39>pPauei7*KMWG",
      "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
    }
  ],
  "total_energy": 2025,
  "u72_router": {
    "all_routes_closed": true,
    "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
    "executed_transition_count": 72,
    "period": 72,
    "router_root_hash72": "/R0jUD5B4mJCII/u<nsN0bMocN/gahJe4I47zMbRT5pPQrz?cp!AG/!(sTwCvxy1TbeMq9)8",
    "routes": [
      {
        "cell_id": "cell:00",
        "phase_index": 1,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:01",
        "phase_index": 10,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:02",
        "phase_index": 19,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:03",
        "phase_index": 28,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:04",
        "phase_index": 37,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:05",
        "phase_index": 46,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:06",
        "phase_index": 55,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:07",
        "phase_index": 56,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:08",
        "phase_index": 65,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:09",
        "phase_index": 2,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:10",
        "phase_index": 11,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:11",
        "phase_index": 20,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:12",
        "phase_index": 29,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:13",
        "phase_index": 38,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:14",
        "phase_index": 47,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:15",
        "phase_index": 48,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:16",
        "phase_index": 57,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:17",
        "phase_index": 66,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:18",
        "phase_index": 3,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:19",
        "phase_index": 12,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:20",
        "phase_index": 21,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:21",
        "phase_index": 30,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:22",
        "phase_index": 39,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:23",
        "phase_index": 40,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:24",
        "phase_index": 49,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:25",
        "phase_index": 58,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:26",
        "phase_index": 67,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:27",
        "phase_index": 4,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:28",
        "phase_index": 13,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:29",
        "phase_index": 22,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:30",
        "phase_index": 31,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:31",
        "phase_index": 32,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:32",
        "phase_index": 41,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:33",
        "phase_index": 50,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:34",
        "phase_index": 59,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:35",
        "phase_index": 68,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:36",
        "phase_index": 5,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:37",
        "phase_index": 14,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:38",
        "phase_index": 23,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:39",
        "phase_index": 24,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:40",
        "phase_index": 33,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:41",
        "phase_index": 42,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:42",
        "phase_index": 51,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:43",
        "phase_index": 60,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:44",
        "phase_index": 69,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:45",
        "phase_index": 6,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:46",
        "phase_index": 15,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:47",
        "phase_index": 16,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:48",
        "phase_index": 25,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:49",
        "phase_index": 34,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:50",
        "phase_index": 43,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:51",
        "phase_index": 52,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:52",
        "phase_index": 61,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:53",
        "phase_index": 70,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:54",
        "phase_index": 7,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:55",
        "phase_index": 8,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:56",
        "phase_index": 17,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:57",
        "phase_index": 26,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:58",
        "phase_index": 35,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:59",
        "phase_index": 44,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:60",
        "phase_index": 53,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:61",
        "phase_index": 62,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:62",
        "phase_index": 71,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:63",
        "phase_index": 0,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:64",
        "phase_index": 9,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:65",
        "phase_index": 18,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:66",
        "phase_index": 27,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:67",
        "phase_index": 36,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:68",
        "phase_index": 45,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:69",
        "phase_index": 54,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:70",
        "phase_index": 63,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:71",
        "phase_index": 64,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:72",
        "phase_index": 1,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:73",
        "phase_index": 10,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:74",
        "phase_index": 19,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:75",
        "phase_index": 28,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:76",
        "phase_index": 37,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:77",
        "phase_index": 46,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:78",
        "phase_index": 55,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:79",
        "phase_index": 56,
        "u72_address_valid": true
      },
      {
        "cell_id": "cell:80",
        "phase_index": 65,
        "u72_address_valid": true
      }
    ],
    "schema": "HHS_U72_TRINARY_PHASE_ROUTER_V1",
    "transition_roots_hash72": [
      "E!WNT*OaCmm8>c1Psz3bQCR61lsT<yF?8EegzFgI<w*EqnXJx(U6/0ZOO!)H?yv3NF1YpGAF",
      "E?VNT*OaCmm8>c1Psz3bQCR61lsT<yF?9DegzFgI<w*EqnXJx(U6/0ZOO!)H?yv3NF2XpGAF",
      "E0UNT*OaCmm8>c1Psz3bQCR61lsT<yF?aCegzFgI<w*EqnXJx(U6/0ZOO!)H?yv3NF3WpGAF",
      "E1TNT*OaCmm8>c1Psz3bQCR61lsT<yF?bBegzFgI<w*EqnXJx(U6/0ZOO!)H?yv3NF4VpGAF",
      "E2SNT*OaCmm8>c1Psz3bQCR61lsT<yF?cAegzFgI<w*EqnXJx(U6/0ZOO!)H?yv3NF5UpGAF",
      "E3RNT*OaCmm8>c1Psz3bQCR61lsT<yF?dzegzFgI<w*EqnXJx(U6/0ZOO!)H?yv3NF6TpGAF",
      "E4QNT*OaCmm8>c1Psz3bQCR61lsT<yF?eyegzFgI<w*EqnXJx(U6/0ZOO!)H?yv3NF7SpGAF",
      "E5PNT*OaCmm8>c1Psz3bQCR61lsT<yF?fxegzFgI<w*EqnXJx(U6/0ZOO!)H?yv3NF8RpGAF",
      "E6ONT*OaCmm8>c1Psz3bQCR61lsT<yF?gwegzFgI<w*EqnXJx(U6/0ZOO!)H?yv3NF9QpGAF",
      "bvJwZ7OaCmm8>c1Psz3bQCR61lsT<yF?hvegzFgI<w*EqnXJx(U6/0ZOO!)H?yv3NF1*vmPF",
      "CRHf4N*tTeoMN6DTAT8I*b<7slzJF!y>DiFfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG2(vng",
      "CRHf5M*tTeoMN6DTAT8I*b<7slzJF!y>DjEfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG2)ung",
      "CRHf6L*tTeoMN6DTAT8I*b<7slzJF!y>DkDfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG2<tng",
      "CRHf7K*tTeoMN6DTAT8I*b<7slzJF!y>DlCfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG2>sng",
      "CRHf8J*tTeoMN6DTAT8I*b<7slzJF!y>DmBfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG2!rng",
      "CRHf9I*tTeoMN6DTAT8I*b<7slzJF!y>DnAfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG2?qng",
      "CRHfaH*tTeoMN6DTAT8I*b<7slzJF!y>DozfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG20png",
      "CRHfbG*tTeoMN6DTAT8I*b<7slzJF!y>DpyfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG21ong",
      "CRHfcF*tTeoMN6DTAT8I*b<7slzJF!y>DqxfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG22nng",
      "CRHg2O*tTeoMN6DTAT8I*b<7slzJF!y>DrwfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG3*wng",
      "CRHg3N*tTeoMN6DTAT8I*b<7slzJF!y>EhFfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG3/vng",
      "CRHg4M*tTeoMN6DTAT8I*b<7slzJF!y>EiEfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG3(ung",
      "CRHg5L*tTeoMN6DTAT8I*b<7slzJF!y>EjDfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG3)tng",
      "CRHg6K*tTeoMN6DTAT8I*b<7slzJF!y>EkCfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG3<sng",
      "CRHg7J*tTeoMN6DTAT8I*b<7slzJF!y>ElBfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG3>rng",
      "CRHg8I*tTeoMN6DTAT8I*b<7slzJF!y>EmAfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG3!qng",
      "CRHg9H*tTeoMN6DTAT8I*b<7slzJF!y>EnzfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG3?png",
      "CRHgaG*tTeoMN6DTAT8I*b<7slzJF!y>EoyfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG30ong",
      "CRHgbF*tTeoMN6DTAT8I*b<7slzJF!y>EpxfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG31nng",
      "CRHh1O*tTeoMN6DTAT8I*b<7slzJF!y>EqwfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG4+wng",
      "CRHh2N*tTeoMN6DTAT8I*b<7slzJF!y>FgFfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG4*vng",
      "CRHh3M*tTeoMN6DTAT8I*b<7slzJF!y>FhEfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG4/ung",
      "CRHh4L*tTeoMN6DTAT8I*b<7slzJF!y>FiDfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG4(tng",
      "CRHh5K*tTeoMN6DTAT8I*b<7slzJF!y>FjCfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG4)sng",
      "CRHh6J*tTeoMN6DTAT8I*b<7slzJF!y>FkBfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG4<rng",
      "CRHh7I*tTeoMN6DTAT8I*b<7slzJF!y>FlAfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG4>qng",
      "CRHh8H*tTeoMN6DTAT8I*b<7slzJF!y>FmzfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG4!png",
      "CRHh9G*tTeoMN6DTAT8I*b<7slzJF!y>FnyfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG4?ong",
      "CRHhaF*tTeoMN6DTAT8I*b<7slzJF!y>FoxfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG40nng",
      "CRHi0O*tTeoMN6DTAT8I*b<7slzJF!y>FpwfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG5-wng",
      "CRHi1N*tTeoMN6DTAT8I*b<7slzJF!y>GfFfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG5+vng",
      "CRHi2M*tTeoMN6DTAT8I*b<7slzJF!y>GgEfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG5*ung",
      "CRHi3L*tTeoMN6DTAT8I*b<7slzJF!y>GhDfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG5/tng",
      "CRHi4K*tTeoMN6DTAT8I*b<7slzJF!y>GiCfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG5(sng",
      "CRHi5J*tTeoMN6DTAT8I*b<7slzJF!y>GjBfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG5)rng",
      "CRHi6I*tTeoMN6DTAT8I*b<7slzJF!y>GkAfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG5<qng",
      "CRHi7H*tTeoMN6DTAT8I*b<7slzJF!y>GlzfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG5>png",
      "CRHi8G*tTeoMN6DTAT8I*b<7slzJF!y>GmyfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG5!ong",
      "CRHi9F*tTeoMN6DTAT8I*b<7slzJF!y>GnxfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG5?nng",
      "CRHj?O*tTeoMN6DTAT8I*b<7slzJF!y>GowfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG6Zwng",
      "CRHj0N*tTeoMN6DTAT8I*b<7slzJF!y>HeFfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG6-vng",
      "CRHj1M*tTeoMN6DTAT8I*b<7slzJF!y>HfEfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG6+ung",
      "CRHj2L*tTeoMN6DTAT8I*b<7slzJF!y>HgDfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG6*tng",
      "CRHj3K*tTeoMN6DTAT8I*b<7slzJF!y>HhCfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG6/sng",
      "CRHj4J*tTeoMN6DTAT8I*b<7slzJF!y>HiBfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG6(rng",
      "CRHj5I*tTeoMN6DTAT8I*b<7slzJF!y>HjAfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG6)qng",
      "CRHj6H*tTeoMN6DTAT8I*b<7slzJF!y>HkzfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG6<png",
      "CRHj7G*tTeoMN6DTAT8I*b<7slzJF!y>HlyfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG6>ong",
      "CRHj8F*tTeoMN6DTAT8I*b<7slzJF!y>HmxfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG6!nng",
      "CRHk!O*tTeoMN6DTAT8I*b<7slzJF!y>HnwfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG7Ywng",
      "CRHk?N*tTeoMN6DTAT8I*b<7slzJF!y>IdFfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG7Zvng",
      "CRHk0M*tTeoMN6DTAT8I*b<7slzJF!y>IeEfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG7-ung",
      "CRHk1L*tTeoMN6DTAT8I*b<7slzJF!y>IfDfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG7+tng",
      "CRHk2K*tTeoMN6DTAT8I*b<7slzJF!y>IgCfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG7*sng",
      "CRHk3J*tTeoMN6DTAT8I*b<7slzJF!y>IhBfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG7/rng",
      "CRHk4I*tTeoMN6DTAT8I*b<7slzJF!y>IiAfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG7(qng",
      "CRHk5H*tTeoMN6DTAT8I*b<7slzJF!y>IjzfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG7)png",
      "CRHk6G*tTeoMN6DTAT8I*b<7slzJF!y>IkyfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG7<ong",
      "CRHk7F*tTeoMN6DTAT8I*b<7slzJF!y>IlxfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG7>nng",
      "CRHl>O*tTeoMN6DTAT8I*b<7slzJF!y>ImwfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG8Xwng",
      "CRHl!N*tTeoMN6DTAT8I*b<7slzJF!y>JcFfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG8Yvng",
      "CRHe9XOtTeoMN6DTAT8I*b<7slzJF!y>JdEfhAGhJ>x/FroYKy)V7(1-PP?<I0zw4OG8Zung"
    ],
    "u0_state_root_hash72": "s(hhJ87tBPLqJ+4jmKzM4c7BUfOLOtMfkkJeSzXcn*8afr8pymYQX5CeO(XGw5FtB4XLb/Xh",
    "u72_equals_u0": true,
    "u72_state_root_hash72": "s(hhJ87tBPLqJ+4jmKzM4c7BUfOLOtMfkkJeSzXcn*8afr8pymYQX5CeO(XGw5FtB4XLb/Xh",
    "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
  },
  "version": "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
}
```
