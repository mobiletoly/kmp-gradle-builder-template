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
use today.

### 1. Prerequisites

1. **Sonatype Central Portal access** – create an OSSRH ticket to register your group id (usually the
   same as your plugin’s package) and enable the Central Portal UI. Once approved you will receive a
   `token`/`password` pair.
2. **PGP signing key** – Central still requires signed publications. Generate a key pair and keep the
   private key/phrase handy:
   ```bash
   gpg --full-generate-key
   gpg --list-secret-keys --keyid-format LONG
   gpg --armor --export <KEY_ID> > private-key.asc
   ```
3. **Gradle secrets** – store all credentials outside the repo (e.g., `~/.gradle/gradle.properties`):
   ```
   mavenCentralUsername=sonatype-token
   mavenCentralPassword=sonatype-secret
   signing.keyId=FFFFFFFF
   signing.password=passphrase-used-for-the-key
   signing.key=contents-of-private-key.asc
   ```
   The Vanniktech plugin automatically picks up these properties when present.

### 2. Gradle configuration

1. Apply the plugin in the root `build.gradle.kts` so every module can inherit it:
   ```kotlin
   plugins {
       id("com.vanniktech.maven.publish") version "0.34.0" apply false
       // existing plugin declarations …
   }
   ```
2. In `plugin/build.gradle.kts`, apply the plugin and describe your coordinates/POM metadata. The
   block below assumes your group id is `dev.example.hello` and your artifact id is
   `kmp-gradle-builder`—adjust to match your actual branding.
   ```kotlin
   plugins {
       kotlin("jvm") version "2.2.21"
       `java-gradle-plugin`
       id("com.vanniktech.maven.publish") version "0.34.0"
   }

   mavenPublishing {
      coordinates("dev.example.hello", "kmp-gradle-builder", version.toString())
       publishToMavenCentral()
       signAllPublications()

       pom {
           name.set("KMP Custom Plugin")
           description.set("Gradle plugin that generates shared KMP sources for Compose Multiplatform")
           url.set("https://github.com/you/your-plugin")
           licenses {
               license {
                   name.set("Apache License 2.0")
                   url.set("https://www.apache.org/licenses/LICENSE-2.0")
               }
           }
           developers {
               developer {
                   id.set("you")
                   name.set("Your Name")
                   email.set("you@example.com")
               }
           }
           scm {
               connection.set("scm:git:https://github.com/you/your-plugin.git")
               developerConnection.set("scm:git:ssh://git@github.com/you/your-plugin.git")
               url.set("https://github.com/you/your-plugin")
           }
       }
   }
   ```
   The existing `gradlePlugin` block stays in place—it registers the plugin id and ensures the plugin
   marker gets published alongside the Maven artifacts. `publishToMavenCentral()` no longer takes a
   host parameter—the plugin now targets the Central Portal by default. We keep the plugin version in
   both the root and the included `plugin/` build so Gradle resolves it even before the root project
   is evaluated; feel free to drop the per-module version if everything lives in a single build.

### 3. Release workflow

1. Update the version in `plugin/build.gradle.kts` (and optionally tag the commit) so Maven Central
   receives immutable coordinates.
2. Run the publish + release task provided by the Vanniktech plugin:
   ```bash
   ./gradlew clean :plugin:publishAndReleaseToMavenCentral
   ```
   For a dry run, drop the `AndRelease` suffix to leave the staging repository open for manual
   inspection inside the Central Portal UI.
3. Watch the release progress in https://central.sonatype.com/. Once the staging repository is
   released, Maven Central mirrors usually update within 10‑20 minutes. The generated artifacts can
   also be reused when publishing to the Gradle Plugin Portal.

Because the Vanniktech plugin codifies the current Central Portal APIs, you avoid wiring the Nexus
publish plugin, manual staging profile ids, or boilerplate signing logic—keeping the deployment
steps minimal and repeatable.
