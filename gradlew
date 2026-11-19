#!/bin/sh

# Minimal Gradle wrapper launcher for Unix-like systems.
APP_HOME=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P) || exit 1
CLASSPATH="$APP_HOME/gradle/wrapper/gradle-wrapper.jar"

if [ -n "$JAVA_HOME" ]; then
    JAVACMD="$JAVA_HOME/bin/java"
else
    JAVACMD="java"
fi

exec "$JAVACMD" \
    -classpath "$CLASSPATH" \
    -Dorg.gradle.appname=gradlew \
    org.gradle.wrapper.GradleWrapperMain "$@"
