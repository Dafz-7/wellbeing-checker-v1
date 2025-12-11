from kivy.uix.screenmanager import Screen

class SignupScreen(Screen):
    def create_account(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        confirm = self.ids.confirm.text.strip()

        if not username or not password:
            print("Missing fields")
            return
        if password != confirm:
            print("Passwords do not match")
            return

        print(f"Account created for {username}")
        self.manager.transition.direction = "right"
        self.manager.current = "login"

    def refresh_page(self):
        self.ids.username.text = ""
        self.ids.password.text = ""
        self.ids.confirm.text = ""
        print("Signup page refreshed")

    def back_to_welcome(self):
        self.manager.transition.direction = "right"
        self.manager.current = "welcome"

    def go_to_settings(self):
        self.manager.transition.direction = "left"
        self.manager.current = "settings"
