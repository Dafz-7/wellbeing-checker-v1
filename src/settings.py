from kivy.uix.screenmanager import Screen
from kivy.app import App

class SettingsScreen(Screen):
    def toggle_theme(self):
        print("Theme toggled (placeholder)")

    def toggle_reminder(self):
        print("Reminder toggled (placeholder)")

    def refresh_page(self):
        print("Settings page refreshed")

    def back_to_welcome(self):
        self.manager.transition.direction = "right"
        self.manager.current = "welcome"

    def go_to_settings(self):
        print("Already in settings")

    def set_timer(self, value):
        try:
            seconds = int(value)
            App.get_running_app().set_session_length(seconds)
        except ValueError:
            print("Invalid timer value")
