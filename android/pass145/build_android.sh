#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
PROJECT="$ROOT/android/pass145"
OUT="$ROOT/release_artifacts/pass145/android"
mkdir -p "$OUT"
missing=()
for cmd in java; do command -v "$cmd" >/dev/null || missing+=("$cmd"); done
[[ -n "${ANDROID_SDK_ROOT:-${ANDROID_HOME:-}}" ]] || missing+=("ANDROID_SDK_ROOT")
if ((${#missing[@]})); then
  printf '{"status":"APK_BUILD_FAILED","error_code":"ANDROID_BUILD_TOOLCHAIN_UNAVAILABLE","missing":[' > "$OUT/APK_BUILD_RECEIPT.json"
  sep=""; for item in "${missing[@]}"; do printf '%s"%s"' "$sep" "$item" >> "$OUT/APK_BUILD_RECEIPT.json"; sep=,; done
  printf '],"fabricated_apk":false}\n' >> "$OUT/APK_BUILD_RECEIPT.json"
  cat "$OUT/APK_BUILD_RECEIPT.json"
  exit 20
fi
if [[ -x "$PROJECT/gradlew" ]]; then GRADLE=("$PROJECT/gradlew"); elif command -v gradle >/dev/null; then GRADLE=(gradle); else echo 'Gradle unavailable' >&2; exit 21; fi
(cd "$PROJECT" && "${GRADLE[@]}" --no-daemon clean assembleDebug)
APK="$PROJECT/app/build/outputs/apk/debug/app-debug.apk"
cp "$APK" "$OUT/hhs-pass145-debug.apk"
sha256sum "$OUT/hhs-pass145-debug.apk" > "$OUT/hhs-pass145-debug.apk.sha256"
printf '{"status":"APK_BUILD_COMPLETED","apk":"hhs-pass145-debug.apk","abi":["arm64-v8a","x86_64"]}\n' > "$OUT/APK_BUILD_RECEIPT.json"
