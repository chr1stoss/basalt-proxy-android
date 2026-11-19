pluginManagement {
    repositories {
        // Maven Central started enforcing stricter request limits in Nov 2026.
        // Use Google's hosted mirror first to keep GitHub Actions dependency
        // resolution reliable, while retaining the canonical repositories as
        // fallbacks for artifacts not mirrored there.
        maven { url = uri("https://maven-central-eu.storage-download.googleapis.com/maven2/") }
        google()
        gradlePluginPortal()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        maven { url = uri("https://maven-central-eu.storage-download.googleapis.com/maven2/") }
        google()
        mavenCentral()
    }
}

rootProject.name = "BasaltProxy"
include(":app")