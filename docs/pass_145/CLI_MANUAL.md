# Pass 145 CLI Manual

The canonical executable is `hhs`; `hhs-android` is an alias. All commands accept `--db PATH` and `--format json|jsonl|text|markdown`.

## Core

```text
hhs status
hhs version
hhs doctor
hhs capabilities
```

## Ingestion and retrieval

```text
hhs ingest file PATH --namespace NAME
hhs ingest directory PATH --recursive
hhs ingest stdin --name NAME
hhs ingest html PATH
hhs ingest javascript PATH
hhs source show SOURCE_ID
hhs source export SOURCE_ID OUTPUT_PATH
hhs object show OBJECT_ID
hhs query "QUESTION"
hhs search TEXT
hhs search O --symbol
hhs graph trace OBJECT_ID
hhs graph contradictions
```

## Validation, replay, and protection

```text
hhs validate source SOURCE_ID
hhs validate object OBJECT_ID
hhs validate database
hhs validate receipt [RECEIPT_ID]
hhs validate replay SOURCE_ID
hhs replay ingestion SOURCE_ID
hhs replay lvm EXECUTION_ID
hhs protect status
hhs protect quarantine OBJECT_ID
hhs protect release OBJECT_ID
```

## Database continuity

```text
hhs database status
hhs database integrity
hhs database compact
hhs database migrate
hhs backup create ARCHIVE
hhs backup verify ARCHIVE
hhs backup inspect ARCHIVE
hhs restore preview ARCHIVE
hhs restore apply ARCHIVE DESTINATION
```

## Enterprise objects

```text
hhs workspace create NAME
hhs workspace inspect WORKSPACE_ID
hhs env create NAME
hhs env clone ENV_ID NEW_NAME
hhs env branch ENV_ID NEW_NAME
hhs env merge SOURCE DESTINATION
hhs script import FILE --language HHS_COMMAND
hhs script paste NAME --language JAVASCRIPT
hhs script validate SCRIPT_ID
hhs script run SCRIPT_ID
hhs lvm create MANIFEST.json
hhs lvm run LVM_ID
hhs api create NAME COLLECTION.json
hhs api execute COLLECTION_ID REQUEST_NAME
hhs extension install MANIFEST.json
```

## Local API

```text
hhs serve --host 127.0.0.1 --port 8765 --token TOKEN --static-root web/pass145
```

Non-loopback binding is rejected by default. Mutating calls require bearer authority and return transaction or execution receipts.
