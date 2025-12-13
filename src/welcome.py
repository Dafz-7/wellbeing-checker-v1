from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.app import App
import random

class WelcomeScreen(Screen):
    greeting = StringProperty("Welcome, user.")
    message = StringProperty("")

    def on_pre_enter(self):
        self.refresh_page()

    def refresh_page(self):
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
        self.manager.transition.direction = "left"
        self.manager.current = "login"

    def go_to_signup(self):
        self.manager.transition.direction = "left"
        self.manager.current = "signup"

    def go_to_settings(self):
        self.manager.transition.direction = "left"
        self.manager.current = "settings"
