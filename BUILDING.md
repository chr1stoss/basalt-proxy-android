# Building Basalt Proxy

## Release APKs with GitHub Actions

The `Android APK Build` workflow builds the Rust native libraries for `arm64-v8a` and
`armeabi-v7a`, runs the Gradle Release build, and uploads the APKs as a workflow artifact.
After pushing the project to GitHub, open **Actions → Android APK Build**, select a
successful run, and download the `basalt-proxy-release-apks` artifact.

The workflow uses the Android SDK/NDK versions selected for this project and does not
require committing generated `.so` files or a signing key.

## Local Windows build

1. Install Android Studio / Android SDK and the Rust toolchain.
2. In `build_so.bat`, set `SDK_PATH` to the Android SDK directory.
3. Run `build_so.bat` to compile the two Android native libraries.
4. Run `gradlew.bat assembleRelease` to build the APK variants.

A private signing key can be configured in `local.properties` with `KEYSTORE_FILE`,
`KEYSTORE_PASSWORD`, `KEY_ALIAS`, and `KEY_PASSWORD`. Without a private keystore, the
Release variant is signed with the standard debug key so it remains installable; that
signature should not be used for publishing updates to an app distributed under a
production signing key.

## Python regression tests

Run the repository checks with:

```bash
python -m unittest discover -s tests -v
```

The GitHub Actions workflow `Python CI` runs the same command on pushes and pull requests.
