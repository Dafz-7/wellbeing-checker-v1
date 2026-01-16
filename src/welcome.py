"""
Welcome Screen for the app.
This screen greets the user and shows a random motivational message.
It also provides navigation to login, signup, and settings screens.
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.app import App
import random

class WelcomeScreen(Screen):
    """
    The first screen shown when the app starts.
    - Displays a greeting (default: "Welcome, user.")
    - Shows a random motivational message each time it is entered
    - Provides navigation buttons to other screens
    """
    greeting = StringProperty("Welcome, user.") # Greeting text shown at the top
    message = StringProperty("") # Motivational message shown below

    def on_pre_enter(self):
        """
        Event triggered before the screen is displayed.
        Refreshes the greeting and motivational message.
        """
        self.refresh_page()

    def refresh_page(self):
        """
        Refresh the greeting and motivational message:
        - If a user is logged in, replace "Welcome, user." with their username.
        - Otherwise, keep the default greeting.
        - Always select a random motivational message from the list.
        """
        app = App.get_running_app()
        if app.current_user_id:  # user is logged in
            # Replace only the "Welcome, user" wording with the username
            self.greeting = f"Welcome, {app.current_username}."
        else:
            self.greeting = "Welcome, user."
        
        # Motivational line: always random
        messages = [
            "Have a nice day!",
            "How’s your day so far? Doing good?",
            "Hope you are feeling good!",
            "Best of luck for today!",
            "Cheer up, will ya!"
        ]
        self.message = random.choice(messages)


    def go_to_login(self):
        """
        Navigate to the Login screen.
        """
        self.manager.transition.direction = "left"
        self.manager.current = "login"

    def go_to_signup(self):
        """
        Navigate to the Signup screen.
        """
        self.manager.transition.direction = "left"
        self.manager.current = "signup"

    def go_to_settings(self):
        """
        Navigate to the Settings screen.
        """
        self.manager.transition.direction = "left"
        self.manager.current = "settings"
