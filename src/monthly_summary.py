from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.app import App
from database import list_all_monthly_summaries
from datetime import datetime

class MonthlySummaryScreen(Screen):
    def on_pre_enter(self):
        self.render_month_list()

    def render_month_list(self):
        app = App.get_running_app()
        user_id = app.current_user_id
        container = self.ids.month_list
        container.clear_widgets()

        months = list_all_monthly_summaries(user_id)
        if not months:
            container.add_widget(Button(text="No summaries yet", size_hint_y=None, height=40))
            return

        for year, month, *_ in months:
            btn = Button(text=f"{year}-{month:02d}", size_hint_y=None, height=40)
            btn.bind(on_release=lambda inst, y=year, m=month: self.open_month(y, m))
            container.add_widget(btn)

    def open_month(self, year, month):
        app = App.get_running_app()
        app.selected_year = year
        app.selected_month = month

        # Show popup message
        month_name = datetime(year, month, 1).strftime("%B %Y")
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=f"Viewing summary for {month_name} now!"))

        ok_btn = Button(text="OK", size_hint_y=None, height=40)
        content.add_widget(ok_btn)

        popup = Popup(title="Summary Selected",
                      content=content,
                      size_hint=(None, None),
                      size=(350, 200),
                      auto_dismiss=False)
        ok_btn.bind(on_release=popup.dismiss)
        popup.open()

        # Navigate back to summary screen with "right" transition
        self.manager.transition.direction = "right"
        self.manager.current = "summary"
