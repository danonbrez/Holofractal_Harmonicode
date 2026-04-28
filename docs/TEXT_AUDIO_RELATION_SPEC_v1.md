# Text Audio Relation Spec v1

Purpose: align text records and audio phase records into one training relation table.

## Records

A text item stores:

- surface: original word or symbol string
- root: consonant-only skeleton
- breath: vowel-only signature
- sound_keys: approximate pronounceable symbols
- phases: 72-ring phase positions
- record_hash72: audit id

An audio item stores:

- stem: x, y, z, w, or closure
- expected_phase_index
- decoded_phase_index
- phase_error
- item_hash72

A relation row stores:

- text_record_hash72
- audio_item_hash72
- relation_kind
- phase_delta
- relation_hash72

## Training packet

The multimodal training packet should contain:

- original text
- text root records
- audio transport manifest
- audio round-trip receipt
- relation rows
- packet_hash72

## Learning objective

The learner compares:

1. surface letters
2. root skeleton
3. breath signature
4. sound key sequence
5. symbolic phase index
6. audio decoded phase index

The stable path is the one with the smallest phase error and consistent text-root relation across repeated passes.
