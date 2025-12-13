from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App
from database import get_entries   # import helper function

class SummaryScreen(Screen):
    def show_summary(self):
        app = App.get_running_app()
        if app.current_user_id is None:
            self._show_popup("Error", "No user logged in.")
            return

        # Fetch entries from database
        rows = get_entries(app.current_user_id)
        if not rows:
            self._show_popup("Info", "No diary entries found.")
            return

        # Build popup with entries
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        for entry, ts in rows[:10]:  # show latest 10 entries
            content.add_widget(Label(text=f"{ts}: {entry[:50]}..."))

        close_btn = Button(text="Close", size_hint_y=None, height=40)
        content.add_widget(close_btn)

        popup = Popup(title="Monthly Summary",
                      content=content,
                      size_hint=(None, None),
                      size=(400, 400),
                      auto_dismiss=False)

        close_btn.bind(on_release=popup.dismiss)
        popup.open()

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
            print("Summary page refreshed")
            popup.dismiss()
            self._show_popup("Success", "Refresh success!")

        def cancel_refresh(instance):
            popup.dismiss()

        yes_btn.bind(on_release=do_refresh)
        no_btn.bind(on_release=cancel_refresh)

        popup.open()

    def _show_popup(self, title, message):
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
        self.manager.transition.direction = "right"
        self.manager.current = "welcome"

    def go_to_settings(self):
        self.manager.transition.direction = "left"
        self.manager.current = "settings"

    def back_to_diary(self):
        self.manager.transition.direction = "right"
        self.manager.current = "diary"
