plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

fun releaseSecret(name: String): String? = providers
    .gradleProperty(name)
    .orElse(providers.environmentVariable(name))
    .orNull
    ?.takeIf { it.isNotBlank() }

val releaseKeystorePath = releaseSecret("PORYADOK5_KEYSTORE_PATH")
val releaseKeystorePassword = releaseSecret("PORYADOK5_KEYSTORE_PASSWORD")
val releaseKeyAlias = releaseSecret("PORYADOK5_KEY_ALIAS")
val releaseKeyPassword = releaseSecret("PORYADOK5_KEY_PASSWORD")
val hasReleaseSigning = listOf(
    releaseKeystorePath,
    releaseKeystorePassword,
    releaseKeyAlias,
    releaseKeyPassword,
).all { it != null }

android {
    namespace = "ru.poryadok5.app"
    compileSdk = 35

    defaultConfig {
        applicationId = "ru.poryadok5.app"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0-rc1"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables.useSupportLibrary = true
    }

    signingConfigs {
        if (hasReleaseSigning) {
            create("releaseUpload") {
                storeFile = file(checkNotNull(releaseKeystorePath))
                storePassword = releaseKeystorePassword
                keyAlias = releaseKeyAlias
                keyPassword = releaseKeyPassword
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            if (hasReleaseSigning) {
                signingConfig = signingConfigs.getByName("releaseUpload")
            }
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
        }
    }

    buildFeatures {
        buildConfig = true
        compose = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    implementation(platform("androidx.compose:compose-bom:2026.04.01"))
    implementation("androidx.activity:activity-compose:1.10.1")
    implementation("androidx.compose.animation:animation")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.compose.foundation:foundation-layout")
    implementation("androidx.compose.material:material-icons-core")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.runtime:runtime-saveable")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.datastore:datastore-preferences:1.1.7")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.9.2")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.10.2")

    debugImplementation("androidx.compose.ui:ui-tooling")

    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20250517")
}

tasks.register("printReleaseSigningStatus") {
    group = "help"
    description = "Prints whether release upload signing inputs are configured."
    doLast {
        if (hasReleaseSigning) {
            println("Release signing: configured via PORYADOK5_* properties/environment.")
            println("Keystore path: $releaseKeystorePath")
        } else {
            println("Release signing: not configured. app-release.aab will be built as an unsigned local RC artifact.")
            println("Required inputs: PORYADOK5_KEYSTORE_PATH, PORYADOK5_KEYSTORE_PASSWORD, PORYADOK5_KEY_ALIAS, PORYADOK5_KEY_PASSWORD")
        }
    }
}
