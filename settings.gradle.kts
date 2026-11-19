pluginManagement {
    repositories {
        // Plugin artifacts from Google are served by Google's Maven repository.
        google()
        // All Maven Central artifacts use Google's public mirror to avoid
        // direct requests to Maven Central's rate-limited endpoint.
        maven { url = uri("https://maven-central-eu.storage-download.googleapis.com/maven2/") }
        // Plugin markers and plugins not hosted in Google Maven / Central.
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        maven { url = uri("https://maven-central-eu.storage-download.googleapis.com/maven2/") }
    }
}

rootProject.name = "BasaltProxy"
include(":app")
