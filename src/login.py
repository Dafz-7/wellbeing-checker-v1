"""
Login Screen for the app.
Handles user authentication, navigation to signup, and refresh/reset of login fields.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App

# Database helpers
from database import check_user, ensure_settings


class LoginScreen(Screen):
    """
    Screen for user login.
    Features:
    - Username/password input
    - Login validation against database
    - Popup messages for success/error
    - Navigation to signup or welcome screen
    - Refresh/reset login fields
    """

    def show_popup(self, title, message):
        """
        Utility function to show a popup with a message.
        Parameters:
        - title: str, popup window title
        - message: str, message displayed inside the popup
        """
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=message))

        close_btn = Button(text="OK", size_hint_y=None, height=40)
        content.add_widget(close_btn)

        popup = Popup(title=title,
                      content=content,
                      size_hint=(None, None),
                      size=(300, 200),
                      auto_dismiss=False)

        # Close popup when OK is pressed
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def login(self):
        """
        Attempt to log in the user:
        - Validate that username and password are provided
        - Check credentials against database
        - If valid:
            * Ensure settings row exists in DB
            * Save user info in App instance
            * Generate monthly summaries silently
            * Apply user-specific timer length
            * Sync Settings screen input if available
            * Show success popup and navigate to Diary screen
        - If invalid:
            * Show error popup
        """
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()

        if not username or not password:
            self.show_popup("Error", "Missing credentials.")
            return

        # Check credentials against database
        user_id = check_user(username, password)
        if user_id:
            ensure_settings(user_id)   # make sure settings row exists

            app = App.get_running_app()
            app.current_user_id = user_id
            app.current_username = username
            app.current_user_display = f"Welcome, {username}"

            # Generate summaries silently for all months
            app.generate_all_summaries(user_id)

            # Load and apply timer_length from DB
            app.apply_user_timer(user_id)

            # Sync Settings screen input if it exists
            if "settings" in [s.name for s in self.manager.screens]:
                settings_screen = self.manager.get_screen("settings")
                if "timer_input" in settings_screen.ids:
                    settings_screen.ids.timer_input.text = str(app.session_length)

            self.show_popup("Success", f"Logged in successfully as {username}!")
            self.manager.transition.direction = "left"
            self.manager.current = "diary"
        else:
            self.show_popup("Error", "Invalid username or password.")

    def signup(self):
        """
        Navigate to the Signup screen.
        """
        self.manager.transition.direction = "left"
        self.manager.current = "signup"

    def refresh_page(self):
        """
        Show confirmation popup before refreshing login fields.
        - If confirmed: clear username and password inputs
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
            """Clear login fields and show success popup."""
            self.ids.username.text = ""
            self.ids.password.text = ""
            print("Login page refreshed")
            popup.dismiss()
            self.show_popup("Success", "Refresh success!")

        def cancel_refresh(instance):
            """Cancel refresh and close popup."""
            popup.dismiss()

        yes_btn.bind(on_release=do_refresh)
        no_btn.bind(on_release=cancel_refresh)
        popup.open()

    def back_to_welcome(self):
        """
        Navigate back to the Welcome screen.
        """
        self.manager.transition.direction = "right"
        self.manager.current = "welcome"