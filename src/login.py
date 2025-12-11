from kivy.uix.screenmanager import Screen

class LoginScreen(Screen):
    def login(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        if username and password:
            print(f"Logging in as {username}")
            self.manager.transition.direction = "left"
            self.manager.current = "diary"
        else:
            print("Missing credentials")

    def signup(self):
        self.manager.transition.direction = "left"
        self.manager.current = "signup"

    def refresh_page(self):
        self.ids.username.text = ""
        self.ids.password.text = ""
        print("Login page refreshed")

    def back_to_welcome(self):
        self.manager.transition.direction = "right"
        self.manager.current = "welcome"

    def go_to_settings(self):
        self.manager.transition.direction = "left"
        self.manager.current = "settings"
