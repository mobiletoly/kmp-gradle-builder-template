plugins {
    kotlin("jvm") version "2.2.21"
    `java-gradle-plugin`
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
        create("kmpProfilesPlugin") {
            id = "dev.goquick.kmpgradlebuilder"
            implementationClass = "dev.goquick.kmpgradlebuilder.KmpProfilesPlugin"
        }
    }
}

tasks.test {
    useJUnitPlatform()
}

kotlin {
    jvmToolchain(17)
}
