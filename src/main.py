from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.clock import Clock
from kivy.properties import StringProperty

# Import your screen classes
from welcome import WelcomeScreen
from login import LoginScreen
from signup import SignupScreen
from diary import DiaryScreen
from summary import SummaryScreen
from settings import SettingsScreen

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

    def build(self):
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
            print("Session expired. Closing app.")
            self.stop()

    def set_session_length(self, seconds):
        if seconds < 20:
            print("Session length too short! Must be at least 20 seconds.")
            return
        if seconds > 30 * 60:
            print("Session length cannot exceed 30 minutes (1800 seconds).")
            return
        self.session_length = seconds
        self.start_session_timer()

if __name__ == "__main__":
    WellbeingApp().run()
