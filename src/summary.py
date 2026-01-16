"""
Summary Screen for the app.
Displays monthly wellbeing summaries with:
- Matplotlib bar chart of sentiment distribution
- Textual insights (average polarity, happiest day, sample diary)
- AI-generated recommendation (threaded for responsiveness)
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.app import App
from datetime import datetime

from kivy_garden.matplotlib import FigureCanvasKivyAgg
import matplotlib.pyplot as plt

# Database helpers
from database import get_entries_for_month, compute_month_stats
# AI helper
from ollama_helper import get_ai_recommendation

import threading


class SummaryScreen(Screen):
    """
    Screen for displaying monthly wellbeing summaries.
    Features:
    - Auto-render summary when entering screen
    - Bar chart visualization of wellbeing distribution
    - Textual insights (average polarity, happiest day, diary snippet)
    - AI recommendation generated in background thread
    - Refresh/reset functionality
    - Navigation to Welcome, Settings, and Diary screens
    """

    def on_pre_enter(self):
        """
        Event triggered before the screen is displayed.
        Automatically renders the current month's summary.
        """
        self.render_current_month_summary()

    def render_current_month_summary(self):
        """
        Render the monthly summary:
        - Fetch diary entries for selected month/year
        - Compute statistics (counts, average polarity, happiest day)
        - Display bar chart of wellbeing distribution
        - Show textual insights
        - Trigger AI recommendation generation
        """
        app = App.get_running_app()
        if app.current_user_id is None:
            self._show_popup("Error", "No user logged in.")
            return

        today = datetime.now()
        year = app.selected_year if app.selected_year is not None else today.year
        month = app.selected_month if app.selected_month is not None else today.month

        rows = get_entries_for_month(app.current_user_id, year, month)
        if not rows:
            self._show_popup("Info", f"No diary entries found for {year}-{month:02d}.")
            return

        stats = compute_month_stats(rows)

        # Clear containers before rendering new summary
        self.ids.chart_box.clear_widgets()
        self.ids.summary_container.clear_widgets()

        # Title label
        self.ids.summary_container.add_widget(
            Label(
                text=f"Monthly Summary: {datetime(year, month, 1).strftime('%B %Y')}",
                size_hint_y=None,
                height=40,
            )
        )

        # Matplotlib bar chart of wellbeing distribution
        labels = ["very sad", "sad", "normal", "happy", "very happy"]
        values = [stats["counts"][l] for l in labels]

        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        ax.bar(labels, values, color=["#c0392b", "#e67e22", "#95a5a6", "#27ae60", "#2ecc71"])
        ax.set_ylabel("Number of days")
        ax.set_title("Wellbeing distribution")
        ax.set_xticklabels(labels, rotation=20, ha="right")
        ax.set_yticks(range(0, max(values) + 1))

        canvas = FigureCanvasKivyAgg(fig)
        canvas.size_hint_y = None
        canvas.height = 450
        self.ids.chart_box.add_widget(canvas)
        plt.close(fig)

        # Textual insights
        info = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=140,
            padding=8,
            spacing=6
        )
        info.add_widget(Label(text=f"Average polarity: {stats.get('avg_polarity', 0):.2f}"))
        if stats.get("happiest_day"):
            info.add_widget(Label(text=f"Happiest day: {stats['happiest_day']}"))
            if stats.get("happiest_entry"):
                info.add_widget(Label(text=f"Diary: {stats['happiest_entry'][:50]}..."))
        else:
            info.add_widget(Label(text="Happiest day: —"))

        self.ids.summary_container.add_widget(info)

        # AI recommendation (threaded for responsiveness)
        self._generate_recommendation(stats)

    def _generate_recommendation(self, stats):
        """
        Generate AI recommendation based on monthly stats.
        - Show loading popup
        - Build prompt with polarity, distribution, happiest day
        - Run AI helper in background thread
        - Fallback message if AI unavailable
        """
        self.loading_popup = Popup(
            title="AI is thinking...",
            content=Label(text="Generating recommendation..."),
            size_hint=(None, None),
            size=(300, 150),
            auto_dismiss=False
        )
        self.loading_popup.open()

        prompt = f"""
        Based on these diary stats:
        - Average polarity: {stats['avg_polarity']:.2f}
        - Distribution: {stats['counts']['happy']} happy days, {stats['counts']['very happy']} very happy days,
        compared to {stats['counts']['sad']} sad days and {stats['counts']['very sad']} very sad days.
        - Happiest day: {stats['happiest_day']}

        Please give the user a short, straight-forward paragraph that reflects the overall trend.
        Celebrate positives if they dominate, but also mention one area to improve.
        Limit to no more than 6 sentences.
        """

        def run_ai():
            ai_text = get_ai_recommendation(prompt)
            if "AI unavailable" in ai_text:
                ai_text = "(Fallback) Keep focusing on your wellbeing and celebrate small wins."

            # Schedule UI update back on main thread
            Clock.schedule_once(lambda dt: self._show_ai_result(ai_text), 0.1)

        threading.Thread(target=run_ai, daemon=True).start()

    def _show_ai_result(self, ai_text):
        """
        Display AI recommendation in summary container.
        - Dismiss loading popup
        - Add styled label with recommendation text
        """
        if hasattr(self, "loading_popup"):
            self.loading_popup.dismiss()

        lbl = Label(
            text=f"Recommendation:\n{ai_text}",
            bold=True,
            color=(0.2, 0.6, 0.2, 1),
            text_size=(self.width - 40, None),
            halign="left",
            valign="top",
            shorten=False,
            size_hint_y=None,
            height=150
        )
        self.ids.summary_container.add_widget(lbl)

    def refresh_page(self):
        """
        Show confirmation popup before refreshing summary.
        - If confirmed: clear summary container, re-render summary
        - If canceled: do nothing
        """
        from kivy.uix.button import Button

        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text="You sure to refresh? All changes will be lost."))

        buttons = BoxLayout(spacing=10, size_hint_y=None, height=40)
        yes_btn = Button(text="Yes")
        no_btn = Button(text="No")
        buttons.add_widget(yes_btn)
        buttons.add_widget(no_btn)
        content.add_widget(buttons)

        popup = Popup(
            title="Confirm Refresh",
            content=content,
            size_hint=(None, None),
            size=(350, 200),
            auto_dismiss=False
        )

        def do_refresh(instance):
            """Clear summary and re-render."""
            if "summary_container" in self.ids:
                self.ids.summary_container.clear_widgets()
            popup.dismiss()
            self.render_current_month_summary()
            self._show_popup("Success", "Refresh success!")

        def cancel_refresh(instance):
            """Cancel refresh and close popup."""
            popup.dismiss()

        yes_btn.bind(on_release=do_refresh)
        no_btn.bind(on_release=cancel_refresh)
        popup.open()

    def _show_popup(self, title, message):
        """
        Utility function to show a popup with a message.
        Parameters:
        - title: str, popup window title
        - message: str, message displayed inside the popup
        """
        from kivy.uix.button import Button
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=message))
        ok_btn = Button(text="OK", size_hint_y=None, height=40)
        content.add_widget(ok_btn)
        popup = Popup(
            title=title,
            content=content,
            size_hint=(None, None),
            size=(300, 200),
            auto_dismiss=False
        )
        ok_btn.bind(on_release=popup.dismiss)
        popup.open()

    def back_to_welcome(self):
        """Navigate back to the Welcome screen."""
        self.manager.transition.direction = "right"
        self.manager.current = "welcome"

    def go_to_settings(self):
        """Navigate to the Settings screen."""
        self.manager.transition.direction = "left"
        self.manager.current = "settings"

    def back_to_diary(self):
        """Navigate back to the Diary screen."""
        self.manager.transition.direction = "right"
        self.manager.current = "diary"