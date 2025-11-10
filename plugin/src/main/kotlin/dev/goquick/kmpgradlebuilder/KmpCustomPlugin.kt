package dev.goquick.kmpgradlebuilder

import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.api.model.ObjectFactory
import org.gradle.api.provider.Property
import org.jetbrains.kotlin.gradle.dsl.KotlinMultiplatformExtension
import org.jetbrains.kotlin.gradle.tasks.KotlinCompilationTask
import javax.inject.Inject

abstract class KmpCustomExtension @Inject constructor(objects: ObjectFactory) {
    val packageName: Property<String> = objects.property(String::class.java)
    val className: Property<String> = objects.property(String::class.java)
    val message: Property<String> = objects.property(String::class.java)
}

class KmpCustomPlugin : Plugin<Project> {
    override fun apply(project: Project) {
        val extension = project.extensions.create("kmpCustom", KmpCustomExtension::class.java).apply {
            packageName.convention("dev.goquick.kmpgradlebuilder.generated")
            className.convention("GeneratedGreeting")
            message.convention("Hello from KMP Custom plugin!")
        }

        val outputDir = project.layout.buildDirectory.dir("generated/src/commonMain/kotlin")
        val generateTask = project.tasks.register(
            "generateKmpCustomSources",
            GenerateKmpCustomTask::class.java
        ) { task ->
            task.group = "code generation"
            task.description = "Generates shared Kotlin sources configured via the kmpCustom extension."
            task.packageName.set(extension.packageName)
            task.className.set(extension.className)
            task.message.set(extension.message)
            task.outputDirectory.set(outputDir)
        }

        project.plugins.withId("org.jetbrains.kotlin.multiplatform") {
            val kotlinExt = project.extensions.getByType(KotlinMultiplatformExtension::class.java)
            kotlinExt.sourceSets.named("commonMain").configure { sourceSet ->
                sourceSet.kotlin.srcDir(generateTask.flatMap { it.outputDirectory })
            }

            project.tasks.withType(KotlinCompilationTask::class.java).configureEach { compileTask ->
                compileTask.dependsOn(generateTask)
            }
        }

        project.tasks.register("kmpCustomDoctor") { task ->
            task.group = "verification"
            task.description = "Prints a short diagnostic about the current Gradle project."
            task.doLast {
                project.logger.lifecycle(
                    "[kmp-gradle-builder-template] package=${extension.packageName.get()}, class=${extension.className.get()}, message=${extension.message.get()}"
                )
            }
        }
    }
}
