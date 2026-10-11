# ============================================================
# FitTrack AI - Buildozer specification
# Run `buildozer -v android debug` to build locally, or push to
# GitHub and let Actions build it via .github/workflows/build.yml.
# ============================================================

[app]

# Application package name (must be unique reverse-DNS, lowercase).
title = FitTrack AI
package.name = fittrack
package.domain = com.fitness.track

# Source file to bundle.
source.filename = main.py
source.dir = .

# Resource directory (icon, splash, presets).
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

# App version (bump when shipping new releases).
version = 1.0.0

# Numeric version codes for the store.
android.numeric_version = 1

# ---------------- Requirements (python-for-android recipes) -----------------
# Keep this list minimal. google-generativeai is NOT included - we call
# the Gemini REST API directly via urllib (built-in), avoiding grpcio /
# protobuf C-extensions that break on Android.
#
# python3 is pinned to 3.11.13 because the default (3.14) is too new
# for Pillow/kivy wheels to exist yet, and p4a's hostpython3 ends up
# creating a Python 3.14 venv that pip can't find packages for.
# kivy/pillow/plyer versions are pinned to ones with wheels for 3.11.
requirements = python3==3.11.13, kivy==2.3.1, pillow==10.4.0, plyer==2.1.0

# ---------------- Permissions ----------------
# CAMERA       -> open the device camera to scan food
# INTERNET     -> call the Gemini REST API
# WRITE_EXTERNAL_STORAGE / READ_EXTERNAL_STORAGE
#              -> allow plyer to write the captured photo
# Note: WRITE_EXTERNAL_STORAGE is auto-deprecated on API 30+, but listing
# it keeps it working on Android 9/10 devices.
android.permissions = CAMERA, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# ---------------- Android API levels ----------------
android.api = 33
android.minapi = 21
android.target_api = 33

# ---------------- Architecture ----------------
# ARM64-v8a covers essentially all modern phones. Add armeabi-v7a for
# older 32-bit devices, x86/x86_64 for emulators. APK size scales
# with the number of architectures.
android.archs = arm64-v8a, armeabi-v7a

# ---------------- UI / Orientation ----------------
orientation = portrait
fullscreen = 0
android.presplash_bg = #111111

# ---------------- Logging ----------------
log_level = 2             # 2 = info

# ---------------- Build details (optional) ----------------
# android.branch = develop
# p4a.branch = develop

# ---------------- Bootstrap & SDL2 ----------------
# bootstrap = sdl2 (Kivy's default, implicit)
# p4a.activity_class_name = org.kivy.android.PythonActivity

# ---------------- Distribution ----------------
# android.release_artifact = apk
# android.keystore = %(source.dir)s/keystore.jks
# android.keyalias = fittrack
# android.keystore_password = ...
# android.keyalias_password = ...

[buildozer]
# Verbosity: 0 minimal, 1 normal, 2 verbose.
verbosity = 2

# Build dir (where intermediate files end up). Local only.
build_dir = ./.buildozer

# Output dir for the APK. Local only.
bin_dir = ./bin