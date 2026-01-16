"""
Monthly Summary Screen for the app.
Displays a list of months with available diary summaries.
Allows user to select a month, shows confirmation popup, and navigates back to Summary screen.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.app import App
from database import list_all_monthly_summaries
from datetime import datetime


class MonthlySummaryScreen(Screen):
    """
    Screen for listing all available monthly summaries.
    Features:
    - Automatically renders month list when entering screen
    - Displays buttons for each month with summaries
    - Shows popup confirmation when a month is selected
    - Navigates back to Summary screen with selected month/year
    """

    def on_pre_enter(self):
        """
        Event triggered before the screen is displayed.
        Renders the list of months with summaries.
        """
        self.render_month_list()

    def render_month_list(self):
        """
        Render the list of months that have summaries:
        - Fetch all months with summaries from DB
        - Clear existing widgets in month_list container
        - Add a button for each month (year-month format)
        - If no summaries exist, show placeholder button
        """
        app = App.get_running_app()
        user_id = app.current_user_id
        container = self.ids.month_list
        container.clear_widgets()

        months = list_all_monthly_summaries(user_id)
        if not months:
            container.add_widget(Button(text="No summaries yet", size_hint_y=None, height=40))
            return

        # Create a button for each month
        for year, month, *_ in months:
            btn = Button(text=f"{year}-{month:02d}", size_hint_y=None, height=40)
            # Bind button to open_month with year/month parameters
            btn.bind(on_release=lambda inst, y=year, m=month: self.open_month(y, m))
            container.add_widget(btn)

    def open_month(self, year, month):
        """
        Handle month selection:
        - Save selected year/month in App instance
        - Show popup message confirming selection
        - Navigate back to Summary screen with 'right' transition
        """
        app = App.get_running_app()
        app.selected_year = year
        app.selected_month = month

        # Show popup message with month name
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

        # Navigate back to summary screen
        self.manager.transition.direction = "right"
        self.manager.current = "summary"