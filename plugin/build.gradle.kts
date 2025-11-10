plugins {
    kotlin("jvm") version "2.2.21"
    `java-gradle-plugin`
    id("com.vanniktech.maven.publish") version "0.34.0"
}

group = "dev.goquick.kmpgradlebuilder"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
    gradlePluginPortal()
}

java {
    toolchain.languageVersion.set(JavaLanguageVersion.of(17))
}

dependencies {
    implementation(gradleApi())
    implementation("org.jetbrains.kotlin:kotlin-gradle-plugin:2.2.21")
    testImplementation(kotlin("test"))
}

gradlePlugin {
    plugins {
        create("kmpCustomPlugin") {
            id = "dev.goquick.kmpgradlebuilder"
            implementationClass = "dev.goquick.kmpgradlebuilder.KmpCustomPlugin"
        }
    }
}

tasks.test {
    useJUnitPlatform()
}

kotlin {
    jvmToolchain(17)
}

mavenPublishing {
    coordinates("dev.goquick.kmpgradlebuilder", "kmp-gradle-builder", version.toString())
    publishToMavenCentral()
    signAllPublications()

    // TODO update with your own metadata (repository, license, etc.)
    pom {
        name.set("KMP Gradle Builder Template Plugin")
        description.set("Gradle plugin that demonstrates generating shared Kotlin sources for KMP projects")
        url.set("https://github.com/goquick/kmp-gradle-builder-template")
        licenses {
            license {
                name.set("Apache License 2.0")
                url.set("https://www.apache.org/licenses/LICENSE-2.0")
            }
        }
        developers {
            developer {
                id.set("goquick")
                name.set("GoQuick")
                email.set("oss@goquick.dev")
            }
        }
        scm {
            connection.set("scm:git:https://github.com/mobiletoly/kmp-gradle-builder-template.git")
            developerConnection.set("scm:git:ssh://git@github.com/mobiletoly/kmp-gradle-builder-template.git")
            url.set("https://github.com/mobiletoly/kmp-gradle-builder-template")
        }
    }
}
