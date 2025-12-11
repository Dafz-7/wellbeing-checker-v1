from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from datetime import datetime
from kivy.clock import Clock

class DiaryScreen(Screen):
    current_datetime = StringProperty("")
    last_entry_date = None  # track last diary entry date

    def on_pre_enter(self):
        self.update_datetime()

    def update_datetime(self, *args):
        now = datetime.now()
        self.current_datetime = now.strftime("%A, %d %B %Y, %I:%M:%S %p")
        delay = 1.0 - (now.microsecond / 1_000_000.0)
        Clock.schedule_once(self.update_datetime, delay)

    def save_entry(self):
        today = datetime.now().date()
        if self.last_entry_date == today:
            print("You already wrote a diary entry today. Only one per day allowed.")
            return

        entry_text = self.ids.entry.text.strip()
        if not entry_text:
            print("Diary entry cannot be empty.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        print(f"Diary entry saved at {timestamp}: {entry_text[:30]}...")
        self.ids.entry.text = ""
        self.last_entry_date = today
