// AGP's plugin implementation and its classpath transitives are resolved
// separately from regular app dependencies. Keep the Central mirror here too.
buildscript {
    repositories {
        google()
        maven { url = uri("https://maven-central-eu.storage-download.googleapis.com/maven2/") }
        gradlePluginPortal()
    }
}

plugins {
    id("com.android.application") version "9.4.0" apply false
    // AGP 9.4.0's default Kotlin Gradle Plugin is 2.2.10; keep the Compose
    // compiler plugin on the same Kotlin version.
    id("org.jetbrains.kotlin.plugin.compose") version "2.2.10" apply false
}
