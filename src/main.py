from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.core.window import Window

# Import layouts
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

# Import your screen classes
from welcome import WelcomeScreen
from login import LoginScreen
from signup import SignupScreen
from diary import DiaryScreen
from summary import SummaryScreen
from settings import SettingsScreen

# Import your database
from database import init_db

class Root(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition()

class WellbeingApp(App):
    title = "Wellbeing-Checker-V1"

    # StringProperty so UI updates automatically
    remaining_time_str = StringProperty("30:00")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session_length = 30 * 60  # default 30 minutes
        self.remaining_time = self.session_length
        self.timer_event = None

        # Track logged-in user
        self.current_user_id = None
        self.current_user_display = "Welcome, user."

    def build(self):
        # Initializes database
        init_db()

        # Load KV files (adjust paths if needed)
        Builder.load_file("ui/welcome.kv")
        Builder.load_file("ui/login.kv")
        Builder.load_file("ui/signup.kv")
        Builder.load_file("ui/diary.kv")
        Builder.load_file("ui/summary.kv")
        Builder.load_file("ui/settings.kv")

        sm = Root()
        sm.add_widget(WelcomeScreen(name="welcome"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(DiaryScreen(name="diary"))
        sm.add_widget(SummaryScreen(name="summary"))
        sm.add_widget(SettingsScreen(name="settings"))

        sm.current = "welcome"

        # Start session timer
        self.start_session_timer()

        # Intercept quit
        Window.bind(on_request_close=self.on_request_close)
        return sm

    def start_session_timer(self):
        self.remaining_time = self.session_length
        if self.timer_event:
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.remaining_time -= 1
        minutes, seconds = divmod(self.remaining_time, 60)
        self.remaining_time_str = f"{minutes:02}:{seconds:02}"

        if self.remaining_time <= 0:
            # Instead of self.stop(), show the extend popup
            self.show_extend_popup()
            # Cancel the timer so it doesn’t keep firing
            if self.timer_event:
                self.timer_event.cancel()
                self.timer_event = None

    def set_session_length(self, seconds):
        if seconds < 20:
            print("Session length too short! Must be at least 20 seconds.")
            return
        if seconds > 30 * 60:
            print("Session length cannot exceed 30 minutes (1800 seconds).")
            return
        self.session_length = seconds
        self.start_session_timer()

    def apply_user_timer(self, user_id):
        """Load timer_length from DB for this user and apply it."""
        from database import get_user_settings
        settings = get_user_settings(user_id)
        if settings and "timer_length" in settings:
            seconds = int(settings["timer_length"])
            self.set_session_length(seconds)

    def on_request_close(self, *args):
        diary_screen = self.root.get_screen("diary")

        diary_text = ""
        entry_saved = False

        if "entry" in diary_screen.ids:
            diary_text = diary_screen.ids.entry.text.strip()
        if hasattr(diary_screen, "entry_saved"):
            entry_saved = diary_screen.entry_saved

        # 1) Typed but not saved
        if diary_text and not entry_saved:
            self.show_quit_popup("Save the entry first!", only_ok=True)
            return True

        # 2) Saved entry (text may be cleared after save)
        if entry_saved:
            self.show_quit_popup("Leaving the app already?...", stay_quit=True)
            return True

        # 3) No diary + timer expired
        if not diary_text and self.remaining_time <= 0:
            self.show_extend_popup()
            return True

        # 4) No diary, still within time limit
        if not diary_text and self.remaining_time > 0:
            self.show_quit_popup("You haven’t written anything yet. Quit anyway?", stay_quit=True)
            return True

        return False  # allow quit
    
    def show_quit_popup(self, message, only_ok=False, stay_quit=False):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=message))

        buttons = BoxLayout(spacing=10, size_hint_y=None, height=40)

        if only_ok:
            ok_btn = Button(text="OK")
            buttons.add_widget(ok_btn)
            content.add_widget(buttons)
            popup = Popup(title="Warning", content=content,
                        size_hint=(None, None), size=(350, 200),
                        auto_dismiss=False)
            ok_btn.bind(on_release=popup.dismiss)

        elif stay_quit:
            stay_btn = Button(text="Stay")
            quit_btn = Button(text="Quit")
            buttons.add_widget(stay_btn)
            buttons.add_widget(quit_btn)
            content.add_widget(buttons)
            popup = Popup(title="Confirm Quit", content=content,
                        size_hint=(None, None), size=(350, 200),
                        auto_dismiss=False)

            stay_btn.bind(on_release=popup.dismiss)
            quit_btn.bind(on_release=lambda inst: super(WellbeingApp, self).stop())

        popup.open()

    def show_extend_popup(self):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text="Time’s up! Add +5 minutes?"))

        buttons = BoxLayout(spacing=10, size_hint_y=None, height=40)
        add_btn = Button(text="Add +5 minutes")
        quit_btn = Button(text="Quit")
        buttons.add_widget(add_btn)
        buttons.add_widget(quit_btn)
        content.add_widget(buttons)

        popup = Popup(title="Session expired", content=content,
                    size_hint=(None, None), size=(350, 200),
                    auto_dismiss=False)

        def extend(instance):
            # Add 5 minutes
            self.set_session_length(300)  # 5 minutes
            popup.dismiss()
            # Show confirmation popup
            self._show_popup("Success", "Added extra 5 minutes!")

        def quit_app(instance):
            popup.dismiss()
            super(WellbeingApp, self).stop()

        add_btn.bind(on_release=extend)
        quit_btn.bind(on_release=quit_app)
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

if __name__ == "__main__":
    WellbeingApp().run()

# 1. implement simple sentiment analysis, and then idk make it somehow analyse each word in the diary database, for every diary in every day iin the month, and analyse it based on these criteria wether the user is (on each day): very, sad, normal, happy, very happy. and using this sentiment analysis, please use this sentiment analysis after each diary is inputted and after that checked whether it falls within those criteria, and then store it the same way as the diary, but different column, and name the column like "wellbeing level" for example.

# 2. implement matplotlib, with this, this visualize the data from every day in each month, that is stored from the database, and read the "wellbeing level" that is done by the sentiment analysis. put this matplotlib in the summary page.

# 3. in the end of every month, please show the summary of the month that is on the database stored from every day input, in the summary page, when the user just logged in into the app.

# 4. if possible, store that whole monthly summary in a dedicated page like the "show monthly summary" from the button, and store the whole monthly summary there, so then the user can repeatedly see their summary.

# 5. to make sure things work for this app, idk how i do it but i need some testing data for this for example, for 3 months at least to see whether the summary or the whole things work as planned or not right? so idk how to do this, how do you think we'll do this?