"""
FitTrack AI - Android-ready build.

Converted from the desktop Kivy app. Key Android adaptations:
- Camera uses Android Intent via plyer (no live preview); the photo
  comes back as a regular file in app-private storage.
- API key is persisted in JsonStore so it survives app restarts.
- SQLite DB lives in app_storage_path() on Android, script dir on desktop.
- ModernButton is a proper ButtonBehavior + Label subclass to avoid the
  Kivy-version-dependent '@ButtonBehavior+Label' shorthand.

Run on desktop (no Android camera): use file picker fallback or skip the
camera step. The build for Android happens via Buildozer on GitHub Actions.
"""

import os
import json
import sqlite3
import datetime
import base64
from io import BytesIO
import urllib.request
import urllib.error

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock

# Pillow is needed to read & re-encode the captured image to a base64 string.
try:
    from PIL import Image  # type: ignore
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# ---- Android / desktop runtime detection ---------------------------------
try:
    from android.storage import app_storage_path  # type: ignore
    ANDROID = True
except ImportError:
    ANDROID = False

try:
    from plyer import camera as plyer_camera      # type: ignore
    PLYER_CAMERA = True
except Exception:
    PLYER_CAMERA = False


APP_DIR = (
    app_storage_path() if ANDROID
    else os.path.dirname(os.path.abspath(__file__))
)
os.makedirs(APP_DIR, exist_ok=True)

DB_PATH = os.path.join(APP_DIR, "fitness_tracker.db")
CAPTURE_PATH = os.path.join(APP_DIR, "capture.jpg")
SETTINGS_PATH = os.path.join(APP_DIR, "settings.json")


# ===========================================================================
# DESIGN LANGUAGE (THE "LOOK")
# ===========================================================================
KV = """
<ModernButton>:
    font_size: '18sp'
    color: [1, 1, 1, 1]
    canvas.before:
        Color:
            rgba: (0.2, 0.6, 0.8, 1) if self.state == 'normal' else (0.1, 0.4, 0.6, 1)
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [15,]

<Card@BoxLayout>:
    orientation: 'vertical'
    padding: 15
    spacing: 10
    canvas.before:
        Color:
            rgba: [0.18, 0.18, 0.18, 1]
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [20,]

<DashboardScreen>:
    canvas.before:
        Color:
            rgba: [0.07, 0.07, 0.07, 1]
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 25
        spacing: 20
        Label:
            text: "FITTRACK"
            font_size: '32sp'
            bold: True
            size_hint_y: None
            height: 50
            color: [0.2, 0.6, 0.8, 1]
        Card:
            size_hint_y: None
            height: 180
            Label:
                text: "DAILY INTAKE"
                font_size: '14sp'
                color: [0.5, 0.5, 0.5, 1]
            Label:
                id: stats_label
                text: "0 / 0 kcal"
                font_size: '36sp'
                bold: True
            Label:
                id: protein_label
                text: "0g Protein"
                font_size: '18sp'
                color: [0.2, 0.6, 0.8, 1]
        Card:
            size_hint_y: None
            height: 80
            Label:
                id: rec_label
                text: "Loading recommendations..."
                font_size: '16sp'
                italic: True
                text_size: self.width, None
                halign: 'center'
        Widget:
            size_hint_y: 1
        BoxLayout:
            size_hint_y: None
            height: 60
            spacing: 15
            ModernButton:
                text: "Food"
                on_release: root.manager.current = 'food'
            ModernButton:
                text: "Weight"
                on_release: root.manager.current = 'weight'
            ModernButton:
                text: "Gym"
                on_release: root.manager.current = 'gym'

<FoodLogScreen>:
    canvas.before:
        Color:
            rgba: [0.07, 0.07, 0.07, 1]
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        Label:
            text: "AI Food Scanner"
            font_size: '26sp'
            bold: True
            size_hint_y: None
            height: 50
        TextInput:
            id: api_input
            hint_text: "Paste Gemini API Key Here"
            multiline: False
            size_hint_y: None
            height: 45
            background_color: [0.2, 0.2, 0.2, 1]
            foreground_color: [1, 1, 1, 1]
        Label:
            id: status_label
            text: "Ready to scan"
            font_size: '14sp'
            color: [0.5, 0.5, 0.5, 1]
            size_hint_y: None
            height: 25
        Image:
            id: preview_image
            size_hint_y: None
            height: 200
            allow_stretch: True
            keep_ratio: True
        ModernButton:
            text: "Open Camera"
            size_hint_y: None
            height: 55
            on_release: root.open_camera()
        ModernButton:
            text: "Analyze Now"
            size_hint_y: None
            height: 55
            on_release: root.analyze_now()
        Widget:
        ModernButton:
            text: "Back"
            size_hint_y: None
            height: 50
            on_release: root.go_back()

<WeightScreen>:
    canvas.before:
        Color:
            rgba: [0.07, 0.07, 0.07, 1]
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 20
        Label:
            text: "Weight Tracker"
            font_size: '28sp'
            bold: True
            size_hint_y: None
            height: 50
        TextInput:
            id: weight_input
            hint_text: "Enter weight in kg"
            multiline: False
            size_hint_y: None
            height: 50
            input_filter: 'float'
            background_color: [0.2, 0.2, 0.2, 1]
            foreground_color: [1, 1, 1, 1]
        ModernButton:
            text: "Save Weight"
            size_hint_y: None
            height: 55
            on_release: root.save_weight()
        Widget:
        ModernButton:
            text: "Back"
            size_hint_y: None
            height: 50
            on_release: root.go_back()

<GymScreen>:
    canvas.before:
        Color:
            rgba: [0.07, 0.07, 0.07, 1]
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        Label:
            text: "Gym Tracker (Coming Soon)"
            font_size: '24sp'
        Widget:
        ModernButton:
            text: "Back"
            size_hint_y: None
            height: 50
            on_release: root.go_back()
"""


# ===========================================================================
# MODERN BUTTON
# ===========================================================================
class ModernButton(ButtonBehavior, Label):
    """Reusable rounded button built from a Label + ButtonBehavior."""
    pass


# ===========================================================================
# DATABASE
# ===========================================================================
class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS profile
                       (id INTEGER PRIMARY KEY, weight REAL,
                        goal TEXT, target_cal REAL, target_prot REAL)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS food_logs
                       (id INTEGER PRIMARY KEY, date TEXT,
                        calories REAL, protein REAL)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS weight_logs
                       (id INTEGER PRIMARY KEY, date TEXT, weight REAL)''')
        cur.execute("SELECT COUNT(*) FROM profile")
        if cur.fetchone()[0] == 0:
            cur.execute(
                "INSERT INTO profile (id, weight, goal, target_cal, target_prot) "
                "VALUES (1, 70.0, 'bulking', 2800.0, 160.0)"
            )
        self.conn.commit()

    def get_profile(self):
        cur = self.conn.cursor()
        cur.execute("SELECT weight, goal, target_cal, target_prot "
                    "FROM profile WHERE id=1")
        return cur.fetchone()

    def save_food(self, cal, prot):
        cur = self.conn.cursor()
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        cur.execute("INSERT INTO food_logs (date, calories, protein) "
                    "VALUES (?, ?, ?)", (date, cal, prot))
        self.conn.commit()

    def get_daily_totals(self):
        cur = self.conn.cursor()
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        cur.execute("SELECT SUM(calories), SUM(protein) FROM food_logs "
                    "WHERE date=?", (date,))
        return cur.fetchone()

    def save_weight(self, weight):
        cur = self.conn.cursor()
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        cur.execute("INSERT INTO weight_logs (date, weight) "
                    "VALUES (?, ?)", (date, weight))
        self.conn.commit()


# ===========================================================================
# GEMINI VISION (REST API - no grpcio/protobuf, Android-friendly)
# ===========================================================================
GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)


class GeminiVisionEngine:
    """Calls Gemini's REST endpoint directly via urllib.

    Avoids the google-generativeai SDK (grpcio / protobuf C extensions) which
    are unreliable on python-for-android. Only depends on PIL for image
    re-encoding.
    """

    def __init__(self, api_key=""):
        self.api_key = api_key

    def set_key(self, api_key):
        self.api_key = api_key

    def _encode_image(self, image_path):
        """Re-encode to JPEG and base64-encode. Smaller payload than PNG."""
        img = Image.open(image_path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        # Cap the longest side at 1024 px to keep payload small.
        img.thumbnail((1024, 1024))
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("ascii")

    def analyze_food_image(self, image_path):
        if not PIL_AVAILABLE:
            return {"error": "Pillow not installed"}
        if not self.api_key or "INSERT" in self.api_key:
            return {"error": "No API key"}
        try:
            b64 = self._encode_image(image_path)
        except Exception as e:
            return {"error": f"Image encode failed: {e}"}

        payload = {
            "contents": [{
                "parts": [
                    {"text": ("Analyze the food in this image. "
                              "Return ONLY this JSON, nothing else, "
                              "no markdown fences: "
                              '{"calories": <number>, "protein": <number>}')},
                    {"inline_data": {
                        "mime_type": "image/jpeg",
                        "data": b64,
                    }},
                ],
            }],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 128,
            },
        }
        body = json.dumps(payload).encode("utf-8")
        url = f"{GEMINI_ENDPOINT}?key={self.api_key}"
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"error": f"Network error: {e.reason}"}
        except Exception as e:
            return {"error": str(e)}

        try:
            data = json.loads(raw)
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            return {"error": f"Bad response: {e}"}

        # Strip optional markdown fences the model sometimes adds.
        clean = text.strip().strip("`")
        if clean.startswith("json"):
            clean = clean[4:].strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            # Last resort: try to extract the first {...} block.
            start = clean.find("{")
            end = clean.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(clean[start:end + 1])
                except json.JSONDecodeError:
                    pass
            return {"error": f"Could not parse: {text[:120]}"}


# ===========================================================================
# SETTINGS (persisted API key)
# ===========================================================================
class SettingsStore:
    def __init__(self):
        self.store = JsonStore(SETTINGS_PATH)

    def get_api_key(self):
        try:
            return self.store.get("api")["key"]
        except KeyError:
            return ""

    def set_api_key(self, key):
        self.store.put("api", key=key)


# ===========================================================================
# SCREENS
# ===========================================================================
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        self.db = kwargs.pop("db", None)
        super().__init__(**kwargs)

    def on_enter(self):
        if not self.db:
            return
        weight, goal, target_cal, target_prot = self.db.get_profile()
        totals = self.db.get_daily_totals()
        curr_cal = totals[0] if totals and totals[0] else 0
        curr_prot = totals[1] if totals and totals[1] else 0
        self.ids.stats_label.text = f"{curr_cal:.0f} / {target_cal:.0f} kcal"
        self.ids.protein_label.text = f"{curr_prot:.1f}g Protein"
        rec = f"Goal: {goal.upper()}\n"
        if curr_cal > target_cal:
            rec += "Over target!"
        elif curr_cal < (target_cal * 0.8):
            rec += "Eat more!"
        else:
            rec += "On track!"
        self.ids.rec_label.text = rec


class FoodLogScreen(Screen):
    def __init__(self, **kwargs):
        self.db = kwargs.pop("db", None)
        self.ve = kwargs.pop("vision_engine", None)
        self.settings = kwargs.pop("settings", None)
        super().__init__(**kwargs)

    def on_enter(self):
        # Pre-fill the API key from persistent settings, if any.
        if self.settings and not self.ids.api_input.text:
            self.ids.api_input.text = self.settings.get_api_key()

    def open_camera(self):
        self.ids.status_label.text = "Opening camera..."
        if not PLYER_CAMERA:
            self.ids.status_label.text = "Camera unavailable on this device"
            return
        try:
            plyer_camera.take_picture(
                filename=CAPTURE_PATH,
                on_complete=self._on_picture_taken,
            )
        except Exception as e:
            self.ids.status_label.text = f"Camera error: {e}"

    def _on_picture_taken(self, success, filename):
        # plyer signature: (success: bool, filename: str)
        # Some Android plyer builds pass just (filename,) — handle both.
        path = filename if isinstance(filename, str) else filename[0]
        Clock.schedule_once(lambda dt: self._after_capture(success, path), 0)

    def _after_capture(self, success, path):
        if not success or not path or not os.path.exists(path):
            self.ids.status_label.text = "Capture failed"
            return
        # Show preview.
        self.ids.preview_image.source = path
        self.ids.preview_image.reload()
        self.ids.status_label.text = "Photo ready. Tap Analyze Now."

    def analyze_now(self):
        # Persist the key the user typed.
        key = self.ids.api_input.text.strip()
        if self.settings:
            self.settings.set_api_key(key)
        if self.ve:
            self.ve.set_key(key)

        if not os.path.exists(CAPTURE_PATH):
            self.ids.status_label.text = "Take a photo first"
            return

        self.ids.status_label.text = "Analyzing with Gemini..."
        # Run on next frame so the UI updates first.
        Clock.schedule_once(lambda dt: self._run_analysis(), 0)

    def _run_analysis(self):
        result = self.ve.analyze_food_image(CAPTURE_PATH) if self.ve else \
                 {"error": "no engine"}
        if isinstance(result, dict) and "error" not in result:
            self.db.save_food(result["calories"], result["protein"])
            self.ids.status_label.text = (
                f"Saved: {result['calories']:.0f} kcal, "
                f"{result['protein']:.1f}g protein"
            )
            self.manager.current = "dashboard"
        else:
            err = result.get("error", "unknown") if isinstance(result, dict) \
                  else "unknown"
            self.ids.status_label.text = f"AI error: {err}"

    def go_back(self):
        self.manager.current = "dashboard"


class WeightScreen(Screen):
    def __init__(self, **kwargs):
        self.db = kwargs.pop("db", None)
        super().__init__(**kwargs)

    def save_weight(self):
        try:
            w = float(self.ids.weight_input.text)
            self.db.save_weight(w)
            self.ids.weight_input.text = ""
        except ValueError:
            pass

    def go_back(self):
        self.manager.current = "dashboard"


class GymScreen(Screen):
    def go_back(self):
        self.manager.current = "dashboard"


# ===========================================================================
# APP
# ===========================================================================
class FitTrackApp(App):
    def build(self):
        Builder.load_string(KV)
        self.db = DatabaseManager()
        self.settings = SettingsStore()
        self.ve = GeminiVisionEngine(api_key=self.settings.get_api_key())

        sm = ScreenManager()
        sm.add_widget(DashboardScreen(db=self.db, name="dashboard"))
        sm.add_widget(FoodLogScreen(
            db=self.db, vision_engine=self.ve,
            settings=self.settings, name="food"))
        sm.add_widget(WeightScreen(db=self.db, name="weight"))
        sm.add_widget(GymScreen(name="gym"))
        return sm


if __name__ == "__main__":
    FitTrackApp().run()