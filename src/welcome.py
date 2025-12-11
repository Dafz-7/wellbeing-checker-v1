from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
import random

class WelcomeScreen(Screen):
    greeting = StringProperty("")

    def on_pre_enter(self):
        self.refresh_page()

    def refresh_page(self):
        messages = [
            "Have a nice day!",
            "How’s your day so far? Doing good?",
            "Hope you are feeling good!",
            "Best of luck for today!",
            "Cheer up, will ya!"
        ]
        self.greeting = random.choice(messages)

    def go_to_login(self):
        self.manager.transition.direction = "left"
        self.manager.current = "login"

    def go_to_signup(self):
        self.manager.transition.direction = "left"
        self.manager.current = "signup"

    def go_to_settings(self):
        self.manager.transition.direction = "left"
        self.manager.current = "settings"
