"""Lightweight regression checks for repository metadata and settings layout."""

from pathlib import Path
import unittest
import re


ROOT = Path(__file__).resolve().parents[1]
SETTINGS_FILE = ROOT / "app/src/main/java/com/basalt/proxy/ui/SettingsTab.kt"


class RepositoryChecks(unittest.TestCase):
    def test_github_links_use_current_owner(self):
        previous_owner = "wh1sper" + "-basalt"
        stale_references = []

        ignored_parts = {".git", ".gradle", "build", "target", "__pycache__"}
        for path in ROOT.rglob("*"):
            if not path.is_file() or ignored_parts.intersection(path.parts):
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if previous_owner in content:
                stale_references.append(str(path.relative_to(ROOT)))

        self.assertEqual(
            stale_references,
            [],
            "Found files containing the previous GitHub owner: "
            + ", ".join(stale_references),
        )

    def test_revealing_settings_are_top_anchored(self):
        source = SETTINGS_FILE.read_text(encoding="utf-8")
        helper_start = source.index("private fun SettingsAnimatedVisibility(")
        helper_end = source.index("@OptIn(ExperimentalMaterial3Api::class)", helper_start)
        helper = source[helper_start:helper_end]

        self.assertIn("expandFrom = Alignment.Top", helper)
        self.assertIn("shrinkTowards = Alignment.Top", helper)
        self.assertEqual(
            source.count("SettingsAnimatedVisibility("),
            4,
            "The shared animation helper should cover its declaration and all "
            "three conditional settings blocks.",
        )
        self.assertEqual(
            len(re.findall(r"(?<!Settings)AnimatedVisibility\(", source)),
            1,
            "Use the shared animation helper so these settings cannot drift "
            "to different expansion anchors.",
        )


    def test_android_workflow_builds_native_libraries_before_apks(self):
        workflow = (ROOT / ".github/workflows/android-build.yml").read_text(encoding="utf-8")
        self.assertIn("cargo ndk -t arm64-v8a --platform 24", workflow)
        self.assertIn("cargo ndk -t armeabi-v7a --platform 23", workflow)
        self.assertIn("./gradlew --no-daemon assembleRelease", workflow)
        self.assertIn("app/build/outputs/apk/*/release/*.apk", workflow)

    def test_android_workflow_does_not_install_removed_legacy_sdk_tools_package(self):
        workflow = (ROOT / ".github/workflows/android-build.yml").read_text(encoding="utf-8")
        self.assertNotRegex(workflow, r"(?m)^\s+uses:\s*android-actions/setup-android@")
        self.assertIn('"$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager"', workflow)
        self.assertIn('"platforms;android-37.0"', workflow)
        self.assertNotIn('"platforms;android-37" \\', workflow)
        self.assertIn('--channel=3', workflow)
        self.assertIn('PLATFORM_VERSIONED="$ANDROID_HOME/platforms/android-37.0"', workflow)
        self.assertIn('if [[ -d "$PLATFORM_VERSIONED" && ! -f "$PLATFORM_AGP/android.jar" ]]; then', workflow)
        self.assertIn('rm -rf "$PLATFORM_AGP"', workflow)
        self.assertIn('ln -s "android-37.0" "$PLATFORM_AGP"', workflow)
        self.assertIn('"ndk;28.2.13676358"', workflow)

    def test_android_17_sdk_package_uses_minor_version_and_agp_alias(self):
        workflow = (ROOT / ".github/workflows/android-build.yml").read_text(encoding="utf-8")
        gradle = (ROOT / "app/build.gradle.kts").read_text(encoding="utf-8")
        self.assertRegex(gradle, r"compileSdk\s*=\s*37")
        self.assertRegex(gradle, r"targetSdk\s*=\s*37")
        self.assertIn('"platforms;android-37.0"', workflow)
        self.assertIn('PLATFORM_AGP="$ANDROID_HOME/platforms/android-37"', workflow)
        self.assertIn('if [[ -d "$PLATFORM_VERSIONED" && ! -f "$PLATFORM_AGP/android.jar" ]]; then', workflow)
        self.assertIn('rm -rf "$PLATFORM_AGP"', workflow)
        self.assertIn('ln -s "android-37.0" "$PLATFORM_AGP"', workflow)


    def test_android_min_sdk_matches_current_androidx_dependencies(self):
        gradle = (ROOT / "app/build.gradle.kts").read_text(encoding="utf-8")
        workflow = (ROOT / ".github/workflows/android-build.yml").read_text(encoding="utf-8")
        arm32 = gradle.split('create("arm32") {', 1)[1].split("        }", 1)[0]
        arm64 = gradle.split('create("arm64") {', 1)[1].split("        }", 1)[0]
        universal = gradle.split('create("universal") {', 1)[1].split("        }", 1)[0]

        self.assertRegex(arm32, r"minSdk\s*=\s*23")
        self.assertRegex(arm64, r"minSdk\s*=\s*24")
        self.assertRegex(universal, r"minSdk\s*=\s*24")
        self.assertIn('implementation("androidx.appcompat:appcompat:1.8.0")', gradle)
        self.assertIn("versionCode = 1337", gradle)
        self.assertIn('versionName = "1.3.3.7"', gradle)
        self.assertIn("cargo ndk -t armeabi-v7a --platform 23", workflow)
        self.assertNotIn("cargo ndk -t armeabi-v7a --platform 21", workflow)

    def test_android_sdk_licenses_do_not_use_a_sigpipe_prone_yes_pipeline(self):
        workflow = (ROOT / ".github/workflows/android-build.yml").read_text(encoding="utf-8")
        self.assertNotRegex(workflow, r"(?m)^\s*yes\s*\|")
        self.assertIn("for _ in {1..100}; do printf 'y\\n'; done > \"$LICENSE_INPUT\"", workflow)
        self.assertIn('"$SDKMANAGER" --licenses < "$LICENSE_INPUT"', workflow)


    def test_gradle_wrapper_is_made_executable_before_release_build(self):
        workflow = (ROOT / ".github/workflows/android-build.yml").read_text(encoding="utf-8")
        build_step = workflow.split("- name: Build Release APKs", 1)[1].split("- name: Upload APK artifacts", 1)[0]
        self.assertIn("chmod +x ./gradlew", build_step)
        self.assertLess(build_step.index("chmod +x ./gradlew"), build_step.index("./gradlew --no-daemon assembleRelease"))
        self.assertIn("test -f gradle/wrapper/gradle-wrapper.jar", build_step)

    def test_maven_central_mirror_is_configured_for_plugin_and_library_resolution(self):
        settings = (ROOT / "settings.gradle.kts").read_text(encoding="utf-8")
        mirror = 'https://maven-central-eu.storage-download.googleapis.com/maven2/'

        plugin_management = settings.split("pluginManagement {", 1)[1].split("dependencyResolutionManagement {", 1)[0]
        dependency_resolution = settings.split("dependencyResolutionManagement {", 1)[1]
        self.assertIn(mirror, plugin_management)
        self.assertIn(mirror, dependency_resolution)
        self.assertLess(plugin_management.index("google()"), plugin_management.index(mirror))
        self.assertLess(dependency_resolution.index("google()"), dependency_resolution.index(mirror))
        self.assertIn("gradlePluginPortal()", plugin_management)
        self.assertNotIn("mavenCentral()", plugin_management)
        self.assertNotIn("mavenCentral()", dependency_resolution)

    def test_root_buildscript_classpath_uses_maven_central_mirror(self):
        build = (ROOT / "build.gradle.kts").read_text(encoding="utf-8")
        self.assertIn("buildscript {", build)
        self.assertIn('maven { url = uri("https://maven-central-eu.storage-download.googleapis.com/maven2/") }', build)
        self.assertLess(build.index("buildscript {"), build.index("plugins {"))

    def test_compose_compiler_plugin_matches_agp_94_default_kotlin_version(self):
        build = (ROOT / "build.gradle.kts").read_text(encoding="utf-8")
        self.assertIn('id("com.android.application") version "9.4.0" apply false', build)
        self.assertIn('id("org.jetbrains.kotlin.plugin.compose") version "2.2.10" apply false', build)
        self.assertNotIn('org.jetbrains.kotlin.plugin.compose") version "2.4.10"', build)

    def test_android_workflow_finds_correct_project_root_even_when_nested(self):
        workflow = (ROOT / ".github/workflows/android-build.yml").read_text(encoding="utf-8")
        self.assertIn("- name: Locate project root with verified Gradle repositories", workflow)
        self.assertIn("find . -maxdepth 6 -type f -name 'settings.gradle.kts'", workflow)
        self.assertIn('&& -f "$candidate/Cargo.toml"', workflow)
        self.assertIn('grep -Fq "$MIRROR" "$settings_file"', workflow)
        self.assertIn('grep -Fq "$MIRROR" "$candidate/build.gradle.kts"', workflow)
        self.assertIn('working-directory: ${{ steps.project-root.outputs.path }}', workflow)
        self.assertIn('path: ${{ steps.project-root.outputs.path }}/app/build/outputs/apk/*/release/*.apk', workflow)

    def test_python_workflow_finds_tests_when_project_is_nested(self):
        workflow = (ROOT / ".github/workflows/python-ci.yml").read_text(encoding="utf-8")
        self.assertIn("Could not locate tests/test_repository_checks.py", workflow)
        self.assertIn("python -m unittest discover -s tests -v", workflow)

    def test_gradle_user_home_cache_is_enabled_in_android_workflow(self):
        workflow = (ROOT / ".github/workflows/android-build.yml").read_text(encoding="utf-8")
        self.assertIn("uses: gradle/actions/setup-gradle@v6", workflow)
        self.assertIn("cache-provider: basic", workflow)
        self.assertLess(workflow.index("uses: gradle/actions/setup-gradle@v6"), workflow.index("./gradlew --no-daemon assembleRelease"))

if __name__ == "__main__":
    unittest.main()
