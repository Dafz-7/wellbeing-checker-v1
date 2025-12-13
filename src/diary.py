from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from datetime import datetime
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App
from database import add_entry   # import helper function

class DiaryScreen(Screen):
    current_datetime = StringProperty("")
    last_entry_date = None  # track last diary entry date
    entry_saved = False

    def on_pre_enter(self):
        # Start updating the clock when entering the screen
        self.update_datetime()
        self.entry_saved = False

    def update_datetime(self, *args):
        # Show exact system time with AM/PM and seconds
        now = datetime.now()
        self.current_datetime = now.strftime("%A, %d %B %Y, %I:%M:%S %p")

        # Align update to the next second boundary
        delay = 1.0 - (now.microsecond / 1_000_000.0)
        Clock.schedule_once(self.update_datetime, delay)

    def save_entry(self):
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

        add_entry(app.current_user_id, entry_text, timestamp)

        self.ids.entry.text = ""
        self.last_entry_date = today
        self.entry_saved = True   # <-- mark as saved
        self._show_popup("Success", "Diary entry saved successfully!")

    def refresh_page(self):
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
            self.ids.entry.text = ""
            self.entry_saved = False
            self.update_datetime()
            print("Diary page refreshed")
            popup.dismiss()
            self._show_popup("Success", "Refresh success!")

        def cancel_refresh(instance):
            popup.dismiss()

        yes_btn.bind(on_release=do_refresh)
        no_btn.bind(on_release=cancel_refresh)

        popup.open()

    def _show_popup(self, title, message):
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
        self.manager.transition.direction = "right"
        self.manager.current = "welcome"

    def go_to_settings(self):
        self.manager.transition.direction = "left"
        self.manager.current = "settings"

    def go_to_summary(self):
        self.manager.transition.direction = "left"
        self.manager.current = "summary"
