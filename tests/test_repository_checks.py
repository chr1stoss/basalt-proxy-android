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
        self.assertIn("cargo ndk -t armeabi-v7a --platform 21", workflow)
        self.assertIn("./gradlew --no-daemon assembleRelease", workflow)
        self.assertIn("app/build/outputs/apk/*/release/*.apk", workflow)



if __name__ == "__main__":
    unittest.main()
