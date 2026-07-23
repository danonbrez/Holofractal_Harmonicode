# HHS Pass 145 Android client

This project builds the governed Android projection of the Pass 145 platform.
It contains a JNI binding to the inherited C runtime and a hardened WebView
client.  The WebView never accesses SQLite or the filesystem directly.  All
knowledge operations traverse the authenticated loopback Pass 145 API.

Build with `./android/pass145/build_android.sh` after installing an Android SDK,
NDK, CMake, and Gradle.  The script emits an explicit failure receipt when the
required toolchain is absent and never fabricates an APK.
