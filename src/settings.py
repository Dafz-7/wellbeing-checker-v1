"""
Settings Screen for the app.
Allows users to configure session timer length and navigate between screens.
Handles:
- Loading saved timer length from database
- Updating timer length with validation
- Refresh/reset functionality
- Popup messages for success/error
"""

from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

# Database helpers
from database import get_user_settings, update_user_settings


class SettingsScreen(Screen):
    """
    Screen for managing user settings.
    Features:
    - Load saved timer length from DB
    - Set new timer length with validation
    - Refresh/reset input field
    - Popup messages for feedback
    - Navigation to Welcome, Diary, and Summary screens
    """

    def on_pre_enter(self):
        """
        Event triggered before the screen is displayed.
        Loads saved timer length from database and displays it in the input field.
        """
        app = App.get_running_app()
        if app.current_user_id:
            settings = get_user_settings(app.current_user_id)
            if settings and "timer_length" in settings:
                if "timer_input" in self.ids:
                    self.ids.timer_input.text = str(settings["timer_length"])

    def refresh_page(self):
        """
        Show confirmation popup before refreshing settings page.
        - If confirmed: clear timer input field
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
            """Clear timer input field and show success popup."""
            if "timer_input" in self.ids:
                self.ids.timer_input.text = ""
            print("Settings page refreshed")
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

    def back_to_diary(self):
        """Navigate back to the Diary screen."""
        self.manager.transition.direction = "right"
        self.manager.current = "diary"

    def back_to_summary(self):
        """Navigate back to the Summary screen."""
        self.manager.transition.direction = "right"
        self.manager.current = "summary"

    def set_timer(self, value):
        """
        Set a new session timer length:
        - Validate input (must be between 20 and 1800 seconds)
        - Apply timer length to app
        - Save updated timer length to DB
        - Show success or error popup
        - Clear input field after success
        """
        try:
            seconds = int(value)
            if seconds < 20 or seconds > 1800:
                self._show_popup("Error", "Session length must be between 20 and 1800 seconds")
                return

            app = App.get_running_app()
            app.set_session_length(seconds)

            # Save to DB
            if app.current_user_id:
                update_user_settings(app.current_user_id, timer_length=seconds)

            self._show_popup("Success", f"Timer set to {seconds} seconds")

            # Clear the input field after success
            if "timer_input" in self.ids:
                self.ids.timer_input.text = ""

        except ValueError:
            self._show_popup("Error", "Invalid timer value")