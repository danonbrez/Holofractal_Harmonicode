# Android Build and Device Validation

## Required toolchain

- JDK 17 or newer;
- Android SDK with platform 35;
- Android build tools including `aapt2`, `d8`, `zipalign`, and `apksigner`;
- Android NDK and CMake 3.22.1;
- Gradle or a checked-in compatible wrapper.

Run:

```text
./android/pass145/build_android.sh
```

The script writes `release_artifacts/pass145/android/APK_BUILD_RECEIPT.json`. It exits nonzero and emits `APK_BUILD_FAILED` when the toolchain is absent. It never creates a placeholder APK.

## Required closure procedure

1. Build twice from a clean tree and compare APK hashes.
2. Verify native libraries for `arm64-v8a` and, where supported, `x86_64`.
3. Install on the supported ARM64 Android device.
4. Launch, load JNI, select a document, use share-to-HHS, ingest offline, restart, inspect persistence, replay ingestion, export backup, restore into an empty target, and test process termination recovery.
5. Record package hash, signing identity, Android version, device ABI, command/API evidence, database root, and receipt roots.

None of these device observations is claimed by the current host evidence package.
