from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App
from database import check_user, ensure_settings

class LoginScreen(Screen):
    def show_popup(self, title, message):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=message))

        close_btn = Button(text="OK", size_hint_y=None, height=40)
        content.add_widget(close_btn)

        popup = Popup(title=title,
                      content=content,
                      size_hint=(None, None),
                      size=(300, 200),
                      auto_dismiss=False)

        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def login(self):
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
        self.manager.transition.direction = "left"
        self.manager.current = "signup"

    def refresh_page(self):
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
            self.ids.username.text = ""
            self.ids.password.text = ""
            print("Login page refreshed")
            popup.dismiss()
            self.show_popup("Success", "Refresh success!")

        def cancel_refresh(instance):
            popup.dismiss()

        yes_btn.bind(on_release=do_refresh)
        no_btn.bind(on_release=cancel_refresh)
        popup.open()

    def back_to_welcome(self):
        self.manager.transition.direction = "right"
        self.manager.current = "welcome"
