from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
import sqlite3
from database import add_user   # import helper function

class SignupScreen(Screen):
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

    def create_account(self):
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
            self.show_popup("Success", f"Account successfully created for {username}!")
            self.manager.transition.direction = "right"
            self.manager.current = "login"
        else:
            self.show_popup("Error", "Username already exists. Please choose another.")

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
            self.ids.confirm.text = ""
            print("Signup page refreshed")
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
            popup.dismiss()

        yes_btn.bind(on_release=do_refresh)
        no_btn.bind(on_release=cancel_refresh)

        popup.open()

    def back_to_welcome(self):
        self.manager.transition.direction = "right"
        self.manager.current = "welcome"
