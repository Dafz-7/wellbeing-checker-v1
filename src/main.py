"""
Main application file for Wellbeing-Checker-V1.
"""

import os
import sys

def resource_path(relative_path):
    """
    Make the absolute path to a resource file.

    This helper ensures that resource files (.kv files, and others) can be
    located both when running the app from source and when packaged with PyInstaller.

    -- Parameters --
    relative_path : str
        The relative path to the resource file (e.g., "ui/welcome.kv").

    -- Returns --
    str
        The absolute path to the resource file, adjusted for PyInstaller's
        temporary directory (_MEIPASS) if applicable.
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.core.window import Window

# Layouts
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

# Screens (import custom screen classes here)
from welcome import WelcomeScreen
from login import LoginScreen
from signup import SignupScreen
from diary import DiaryScreen
from summary import SummaryScreen
from settings import SettingsScreen
from monthly_summary import MonthlySummaryScreen

# Database helpers
from database import (
    init_db,
    get_user_settings,
    get_entries_for_month,
    compute_month_stats,
    upsert_monthly_summary,
)

from datetime import datetime


class Root(ScreenManager):
    """
    Root screen manager that controls nagivation between different screen.
    Uses the class SlideTransition in Kivy for smooth screen transition.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition()


class WellbeingApp(App):
    """
    Main application class for this app.
    Handles:
    - Session timer
    - User login and signup
    - Monthly summary generation
    - Popup dialogs
    """
    title = "Wellbeing-Checker-V1"
    remaining_time_str = StringProperty("30:00")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Default session length is 30 minutes
        self.session_length = 30 * 60
        self.remaining_time = self.session_length
        self.timer_event = None

        # Track logged-in user
        self.current_user_id = None
        self.current_user_display = "Welcome, user."

        # Track selected month for summaries
        self.selected_year = None
        self.selected_month = None

    def build(self):
        """
        Build the application:
        - Initialize database
        - Load KV files for UI
        - Add all screen to the ScreenManager
        - Start session timer
        - Bind quit event
        """

        # Initialize database
        init_db()

        # Load KV files
        """Using the resource_path() function at the top on these
        KV file making sure they work after packaged with PyInstaller."""
        Builder.load_file(resource_path("ui/welcome.kv"))
        Builder.load_file(resource_path("ui/login.kv"))
        Builder.load_file(resource_path("ui/signup.kv"))
        Builder.load_file(resource_path("ui/diary.kv"))
        Builder.load_file(resource_path("ui/summary.kv"))
        Builder.load_file(resource_path("ui/settings.kv"))
        Builder.load_file(resource_path("ui/monthly_summary.kv"))


        sm = Root()
        sm.add_widget(WelcomeScreen(name="welcome"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(DiaryScreen(name="diary"))
        sm.add_widget(SummaryScreen(name="summary"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(MonthlySummaryScreen(name="monthly_summary"))

        sm.current = "welcome"

        # Start session timer
        self.start_session_timer()

        # Intercept quit
        Window.bind(on_request_close=self.on_request_close)
        return sm

    # ---------------- Timer Management ----------------
    def start_session_timer(self):
        """Start or restart the session timer."""
        self.remaining_time = self.session_length
        if self.timer_event:
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        """Update timer every second and show extend popup when timer ends."""
        self.remaining_time -= 1
        minutes, seconds = divmod(self.remaining_time, 60)
        self.remaining_time_str = f"{minutes:02}:{seconds:02}"

        if self.remaining_time <= 0:
            self.show_extend_popup()
            if self.timer_event:
                self.timer_event.cancel()
                self.timer_event = None

    def set_session_length(self, seconds):
        """Set session length with validation (20-1800 seconds)."""
        if seconds < 20:
            print("Session length too short! Must be at least 20 seconds.")
            return
        if seconds > 30 * 60:
            print("Session length cannot exceed 30 minutes (1800 seconds).")
            return
        self.session_length = seconds
        self.start_session_timer()

    def apply_user_timer(self, user_id):
        """Load timer_length from DB for this user and apply it."""
        settings = get_user_settings(user_id)
        if settings and "timer_length" in settings:
            seconds = int(settings["timer_length"])
            self.set_session_length(seconds)

    # ---------------- Monthly Summary ----------------
    def generate_all_summaries(self, user_id):
        """
        Generate summaries for all months that have diary entries.
        Queries DB for distinct months, computes stats, and saves summaries.
        """
        import sqlite3
        conn = sqlite3.connect("wellbeing.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT substr(timestamp, 1, 4) AS year,
                            substr(timestamp, 6, 2) AS month
            FROM diary
            WHERE user_id = ?
            ORDER BY year, month
        """, (user_id,))
        months = cursor.fetchall()
        conn.close()

        for y, m in months:
            rows = get_entries_for_month(user_id, int(y), int(m))
            if rows:
                stats = compute_month_stats(rows)
                upsert_monthly_summary(user_id, int(y), int(m), stats)

    # ---------------- Quit / Popup Management ----------------
    def on_request_close(self, *args):
        """
        Handle quit requests:
        - Warn user if unsaved diary entry exists
        - Confirm quit if entry saved or already in DB
        - Show extend popup if timer expired
        - Allow quit otherwise
        """
        diary_screen = self.root.get_screen("diary")

        diary_text = ""
        if "entry" in diary_screen.ids:
            diary_text = diary_screen.ids.entry.text.strip()

        entry_saved = getattr(diary_screen, "entry_saved", False)

        # Check database for today's entry
        has_today_entry = False
        if self.current_user_id:
            today_str = datetime.now().strftime("%Y-%m-%d")
            year = datetime.now().year
            month = datetime.now().month
            rows = get_entries_for_month(self.current_user_id, year, month)
            # rows = [(entry, timestamp, wellbeing_level, polarity), ...] and so on based on what's in the database
            has_today_entry = any(r[1].startswith(today_str) for r in rows)

        """If the user wrote the diary but have not yet saved:"""
        if diary_text and not entry_saved:
            self.show_quit_popup("Save the entry first!", only_ok=True)
            return True

        """If the user wrote and saved the diary but wants to quit:"""
        if entry_saved or has_today_entry:
            self.show_quit_popup("Leaving the app already?...", stay_quit=True)
            return True

        """If the user not yet wrote diary but timer runs out:"""
        if not diary_text and self.remaining_time <= 0:
            self.show_extend_popup()
            return True

        """If the user not yet wrote diary but wants to quit:"""
        if not diary_text and self.remaining_time > 0:
            self.show_quit_popup("You haven’t written anything yet. Quit anyway?", stay_quit=True)
            return True

        return False  # Allow quit

    def show_quit_popup(self, message, only_ok=False, stay_quit=False):
        """Show quit confirmation popup with different button options."""
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=message))

        buttons = BoxLayout(spacing=10, size_hint_y=None, height=40)

        if only_ok:
            ok_btn = Button(text="OK")
            buttons.add_widget(ok_btn)
            content.add_widget(buttons)
            popup = Popup(title="Warning", content=content,
                          size_hint=(None, None), size=(350, 200),
                          auto_dismiss=False)
            ok_btn.bind(on_release=popup.dismiss)

        elif stay_quit:
            stay_btn = Button(text="Stay")
            quit_btn = Button(text="Quit")
            buttons.add_widget(stay_btn)
            buttons.add_widget(quit_btn)
            content.add_widget(buttons)
            popup = Popup(title="Confirm Quit", content=content,
                          size_hint=(None, None), size=(350, 200),
                          auto_dismiss=False)

            stay_btn.bind(on_release=popup.dismiss)
            quit_btn.bind(on_release=lambda inst: super(WellbeingApp, self).stop())

        popup.open()

    def show_extend_popup(self):
        """Show popup when session expires, offering +5 minutes or quit."""
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text="Time’s up! Add +5 minutes?"))

        buttons = BoxLayout(spacing=10, size_hint_y=None, height=40)
        add_btn = Button(text="Add +5 minutes")
        quit_btn = Button(text="Quit")
        buttons.add_widget(add_btn)
        buttons.add_widget(quit_btn)
        content.add_widget(buttons)

        popup = Popup(title="Session expired", content=content,
                      size_hint=(None, None), size=(350, 200),
                      auto_dismiss=False)

        def extend(instance):
            """
            Extend the session by 5 minutes:
            - Resets session length to 300 seconds
            - Dismisses popup
            - Shows confirmation popup
            """
            self.set_session_length(300)  # 5 minutes
            popup.dismiss()
            self._show_popup("Success", "Added extra 5 minutes!")

        def quit_app(instance):
            """
            Quit the application immediately:
            - Dismisses pop up
            - Stops the app and the Kivy itself
            """
            popup.dismiss()
            super(WellbeingApp, self).stop()

        # Bind buttons to actions
        add_btn.bind(on_release=extend)
        quit_btn.bind(on_release=quit_app)
        popup.open()

    def _show_popup(self, title, message):
        """
        Utility function to show a simple popup with a message.
        Parameter:
        - title: str, popup window title
        - message: str, message displayed inside the popup
        """
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=message))

        ok_btn = Button(text="OK", size_hint_y=None, height=40)
        content.add_widget(ok_btn)

        popup = Popup(title=title,
                      content=content,
                      size_hint=(None, None),
                      size=(300, 200),
                      auto_dismiss=False)

        ok_btn.bind(on_release=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    
    # The starting of the app
    WellbeingApp().run()
