"""
Diary Screen for the app.
Allows users to write daily diary entries, runs sentiment analysis, and saves entries to the database.
Also displays current date/time and provides navigation to other screens.
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from datetime import datetime
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App

# Database helper and sentiment analyzer
from database import add_entry_with_sentiment
from sentiment_simple import analyze_sentiment


class DiaryScreen(Screen):
    """
    Screen for writing and saving diary entries.
    Features:
    - Displays current date and time (auto-updating every second)
    - Allows one diary entry per day per user
    - Runs sentiment analysis on entry text
    - Saves entry with wellbeing level and polarity to database
    - Provides navigation to Welcome, Settings, and Summary screens
    """
    current_datetime = StringProperty("")  # Current system time displayed in UI
    last_entry_date = None                 # Track last diary entry date
    entry_saved = False                    # Flag to check if entry was saved

    def on_pre_enter(self):
        """
        Event triggered before the screen is displayed.
        - Starts updating the clock
        - Resets entry_saved flag
        """
        self.update_datetime()
        self.entry_saved = False

    def update_datetime(self, *args):
        """
        Update the current date/time string every second.
        - Shows exact system time with AM/PM and seconds
        - Aligns update to the next second boundary
        """
        now = datetime.now()
        self.current_datetime = now.strftime("%A, %d %B %Y, %I:%M:%S %p")

        # Align update to the next second boundary
        delay = 1.0 - (now.microsecond / 1_000_000.0)
        Clock.schedule_once(self.update_datetime, delay)

    def save_entry(self):
        """
        Save a diary entry for the current user:
        - Ensure only one entry per day
        - Validate that entry is not empty
        - Run sentiment analysis on entry text
        - Save entry with timestamp, wellbeing level, and polarity to DB
        - Show success or error popup
        """
        today = datetime.now().date()
        if self.last_entry_date == today:
            self._show_popup("Error", "You already wrote a diary entry today. Only one per day allowed.")
            return

        entry_text = self.ids.entry.text.strip()
        if not entry_text:
            self._show_popup("Error", "Diary entry cannot be empty.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

        app = App.get_running_app()
        if app.current_user_id is None:
            self._show_popup("Error", "No user logged in.")
            return

        # Run simple sentiment analysis
        wellbeing_level, polarity = analyze_sentiment(entry_text)

        # Save to database with wellbeing level
        success = add_entry_with_sentiment(app.current_user_id, entry_text, timestamp, wellbeing_level, polarity)

        if not success:
            # Duplicate entry for this user/date
            self._show_popup("Error", "You already wrote a diary entry today. Only one per day allowed.")
            return

        # Clear field and mark entry saved
        self.ids.entry.text = ""
        self.last_entry_date = today
        self.entry_saved = True
        self._show_popup(
            "Success",
            f"Diary entry saved!\nWellbeing level: {wellbeing_level}\nPolarity: {polarity:.2f}"
        )

    def refresh_page(self):
        """
        Show confirmation popup before refreshing diary entry field.
        - If confirmed: clear entry field, reset entry_saved flag, update datetime
        - If canceled: do nothing
        """
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text="You sure to refresh? All changes will be lost."))

        buttons = BoxLayout(spacing=10, size_hint_y=None, height=40)
        yes_btn = Button(text="Yes")
        no_btn = Button(text="No")
        buttons.add_widget(yes_btn)
        buttons.add_widget(no_btn)
        content.add_widget(buttons)

        popup = Popup(title="Confirm Refresh",
                      content=content,
                      size_hint=(None, None),
                      size=(350, 200),
                      auto_dismiss=False)

        def do_refresh(instance):
            """Clear diary entry and reset state."""
            self.ids.entry.text = ""
            self.entry_saved = False
            self.update_datetime()
            popup.dismiss()
            self._show_popup("Success", "Refresh success!")

        def cancel_refresh(instance):
            """Cancel refresh and close popup."""
            popup.dismiss()

        yes_btn.bind(on_release=do_refresh)
        no_btn.bind(on_release=cancel_refresh)

        popup.open()

    def _show_popup(self, title, message):
        """
        Utility function to show a popup with a message.
        Parameters:
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

    def back_to_welcome(self):
        """Navigate back to the Welcome screen."""
        self.manager.transition.direction = "right"
        self.manager.current = "welcome"

    def go_to_settings(self):
        """Navigate to the Settings screen."""
        self.manager.transition.direction = "left"
        self.manager.current = "settings"

    def go_to_summary(self):
        """Navigate to the Summary screen."""
        self.manager.transition.direction = "left"
        self.manager.current = "summary"