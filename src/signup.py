"""
Signup Screen for the app.
Handles user account creation, validation, and navigation back to welcome/login screens.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App

import sqlite3
from database import add_user, get_user_id   # get_user_id fetches the new user's ID after signup


class SignupScreen(Screen):
    """
    Screen for user signup.
    Features:
    - Username/password input with confirmation
    - Account creation and validation
    - Popup messages for success/error
    - Refresh/reset signup fields
    - Navigation back to welcome screen
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

    def create_account(self):
        """
        Create a new user account:
        - Validate that username, password, and confirmation are provided
        - Ensure password and confirmation match
        - Attempt to add user to database
        - If successful:
            * Fetch new user ID
            * Save user info in App instance
            * Generate monthly summaries for user
            * Show success popup and navigate to Login screen
        - If username already exists:
            * Show error popup
        """
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        confirm = self.ids.confirm.text.strip()

        if not username or not password:
            self.show_popup("Error", "Missing fields.")
            return
        if password != confirm:
            self.show_popup("Error", "Passwords do not match.")
            return

        # Try to add user to database
        success = add_user(username, password)
        if success:
            # Fetch the new user's ID
            new_user_id = get_user_id(username)

            # Set current user in the app and generate summaries
            app = App.get_running_app()
            app.current_user_id = new_user_id
            app.current_user_display = f"Welcome, {username}!"
            app.generate_all_summaries(new_user_id)

            self.show_popup("Success", f"Account successfully created for {username}!")
            # After signup, go to login screen (or directly to summary if preferred)
            self.manager.transition.direction = "right"
            self.manager.current = "login"
        else:
            self.show_popup("Error", "Username already exists. Please choose another.")

    def refresh_page(self):
        """
        Show confirmation popup before refreshing signup fields.
        - If confirmed: clear username, password, and confirm inputs
        - Show success popup after refresh
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
            """Clear signup fields and show success popup."""
            self.ids.username.text = ""
            self.ids.password.text = ""
            self.ids.confirm.text = ""
            popup.dismiss()

            success_content = BoxLayout(orientation="vertical", spacing=10, padding=10)
            success_content.add_widget(Label(text="Refresh success!"))

            ok_btn = Button(text="OK", size_hint_y=None, height=40)
            success_content.add_widget(ok_btn)

            success_popup = Popup(title="Success",
                                  content=success_content,
                                  size_hint=(None, None),
                                  size=(300, 200),
                                  auto_dismiss=False)

            ok_btn.bind(on_release=success_popup.dismiss)
            success_popup.open()

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