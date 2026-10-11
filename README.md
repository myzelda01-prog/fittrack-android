# FitTrack AI — Android build

Kivy calorie & weight tracker, packaged as an Android APK via **Buildozer** and **GitHub Actions** (no Linux required locally).

The whole project is in `main.py` (single-file app, KV inline). `buildozer.spec` declares the Android build settings. `.github/workflows/build.yml` runs the build on GitHub's free Linux runners and uploads the resulting `fittrack-debug-apk` artifact.

## What changed vs. the original desktop app

| Original (desktop) | Android version |
|---|---|
| `cv2.VideoCapture(0)` live preview | Native camera intent via `plyer.camera.take_picture()` — no live preview, photo shows as a still image |
| `google.generativeai` SDK (grpcio/protobuf) | Direct REST call to `generativelanguage.googleapis.com` via `urllib` — no C extensions, smaller APK |
| SQLite in script directory | SQLite in Android app-private storage (`app_storage_path()`) |
| API key re-entered each session | API key persisted via Kivy `JsonStore` |
| `<ModernButton@ButtonBehavior+Label>` shorthand | Explicit `class ModernButton(ButtonBehavior, Label):` (Kivy-version-safe) |

## How to build the APK (Windows, no Linux needed)

1. **Create a new GitHub repo** and push this folder:
   ```powershell
   cd C:\Users\Thomas\Desktop\Projets_AI\Calorie_Tracker_for_Phone
   git init
   git add .
   git commit -m "Initial FitTrack Android build"
   git branch -M main
   git remote add origin https://github.com/<you>/<repo>.git
   git push -u origin main
   ```

2. **Wait for the workflow to finish** (or trigger it manually):
   - Open the repo on GitHub → **Actions** tab → `Build Android APK` → **Run workflow**.

3. **Download the APK** from the workflow run:
   - Open the run → scroll to **Artifacts** → download `fittrack-debug-apk.zip`
   - Unzip it → the `.apk` is inside.

4. **Install on your Android phone**:
   - Transfer the APK to the phone (USB, Drive, email attachment, etc.).
   - On the phone, enable **Settings → Apps → Special access → Install unknown apps** for your file manager / browser.
   - Open the APK with the file manager → **Install**.

The first build takes ~20–30 min (downloading Android SDK/NDK). Subsequent builds with the same `buildozer.spec` are ~5–10 min thanks to caching.

## How to test on Windows desktop before building

```powershell
pip install kivy pillow plyer
python main.py
```

Note: the camera button won't work on desktop (no Android intent). Everything else (weight, dashboard, settings persistence) works.

To get a Gemini API key, grab one from <https://aistudio.google.com/app/apikey>.

## Troubleshooting

- **"No API key"** → tap the Food screen, paste your Gemini key once, it persists.
- **Camera does nothing on desktop** → expected. Use the Android APK.
- **APK won't install on phone** → your device must allow installs from unknown sources; the APK is debug-signed (not Play Store ready).
- **Build fails in Actions** → download the `build-log` artifact and check the trace.

## Release / Play Store

The CI currently builds a **debug** APK (signed with the debug key, easy to install). For Play Store you need a release APK signed with your own keystore. See the commented-out `android.keystore_*` lines in `buildozer.spec` and Buildozer's [Android signing docs](https://buildozer.readthedocs.io/en/latest/quickstart.html#packaging-your-application-for-android).