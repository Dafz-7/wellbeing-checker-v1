from kivy.uix.screenmanager import Screen

class SummaryScreen(Screen):
    def show_summary(self):
        print("Showing monthly summary (placeholder)")

    def refresh_page(self):
        print("Summary page refreshed")

    def back_to_welcome(self):
        self.manager.transition.direction = "right"
        self.manager.current = "welcome"

    def go_to_settings(self):
        self.manager.transition.direction = "left"
        self.manager.current = "settings"

    def go_to_diary(self):
        self.manager.transition.direction = "right"
        self.manager.current = "diary"
