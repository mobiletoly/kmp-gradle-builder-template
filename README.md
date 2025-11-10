# KMP Plugin Template

This repository is a Kotlin Multiplatform **KMP Gradle plugin template**. Use it when you want to
build and distribute your own Gradle plugin tailored for KMP projects. We provide:

- `plugin/` – a Gradle plugin module that currently generates a simple “hello world” Kotlin source
  file. It shows how to register a custom task, expose extension properties, and hook generated
  sources into a KMP project.
- `sample-app` – a Compose Multiplatform sample that consumes the plugin, proving the
  generated sources are compiled for Android, desktop, and iOS.

You can treat this repo as scaffolding for **your own Gradle plugin**: rename things with the
provided script, extend the plugin logic (tasks, validations, convention plugins, etc.), and keep
the sample app as an integration test while you iterate.

## Requirements

- JDK 17+
- Python 3.9+ (for the project generator script)

## Using the Template Script

The `tools/setup_template.py` script copies this repository to a new location and rewrites all
occurrences of the default package/plugin id so you can start a fresh plugin without manual
search‑and‑replace.

Run it from the repository root:

```bash
python tools/setup_template.py \
  --plugin-id dev.example.hello \
  --package-name dev.example.hello \
  --plugin-name HelloCustom \
  --project-name hello-plugin \
  --output-dir ~/work/hello-plugin
```

Arguments:

- `--plugin-id` – Gradle plugin id that will be registered in `plugin/build.gradle.kts` and applied
  in the sample module (e.g., `dev.example.hello`).
- `--package-name` – Kotlin package used for plugin sources and the sample application (e.g.,
  `dev.example.hello`).
- `--project-name` – Optional root project name. Defaults to the last segment of the plugin id.
- `--plugin-name` – Optional CamelCase display/class name (default `KmpCustom`). Used for the
  generated plugin/extension/task classes plus the DSL block name (e.g., `helloCustom { }`).
- `--output-dir` – Directory where the generated project is written. It must not already exist.

The script performs the following:

1. Copies the current repo to the target directory (excluding `.git` and previous build artifacts).
2. Removes transient directories such as `build/`, `.gradle/`, `sample-app/iosApp/Frameworks`, etc.
3. Renames package directories and updates imports/package declarations.
4. Updates `settings.gradle.kts` with the provided project name.

After it completes:

```bash
cd ~/work/hello-plugin
./gradlew :plugin:build
./gradlew :sample-app:composeApp:build
```

You now have an isolated repository that still includes the example Compose app and iOS host but
uses your plugin id/package. From there you can:

- Expand the plugin logic (tasks, extensions, validations)
- Modify or remove the sample app
- Re‑initialize Git (`git init`) and push to your own origin

## Publishing to Maven Central

For distribution we recommend the community-backed
[`com.vanniktech.maven.publish`](https://vanniktech.github.io/gradle-maven-publish-plugin/central/)
plugin. It wraps the standard `maven-publish` + `signing` setup, drives the new Maven Central Portal
workflow end-to-end, and is what many Kotlin Multiplatform templates (including JetBrains’ wizard)
use today. This project already has vanniktech plugin applied and configured.
