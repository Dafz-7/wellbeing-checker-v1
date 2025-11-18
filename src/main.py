import kivy
from kivy.app import App

from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

class MyGridLayout(GridLayout):
    def __init__(self, **kwargs):
        super(MyGridLayout, self).__init__(**kwargs)

        self.cols = 1

        self.top_grid = GridLayout()
        self.top_grid.cols = 2

        self.bottom_grid = GridLayout()
        self.bottom_grid.cols = 1

        self.add_widget(self.top_grid)
        self.add_widget(self.bottom_grid)

        self.username = Label(
            text="Enter your username:"
        )

        self.password = Label(
            text="Enter your password:"
        )

        self.top_grid.add_widget(self.username)
        self.textinput_username = TextInput(
            multiline=False
        )
        self.top_grid.add_widget(self.textinput_username)
        
        self.top_grid.add_widget(self.password)
        self.textinput_password = TextInput(
            multiline=False
        )
        self.top_grid.add_widget(self.textinput_password)

        self.submit_button = Button(
            text="Submit"
        )

        self.bottom_grid.add_widget(self.submit_button)

        self.submit_button.bind(
            on_press=self.press
        )

    def press(self, instance):
        username = self.textinput_username.text
        password = self.textinput_password.text

        self.bottom_grid.add_widget(
            Label(
                text=f"Your username is: {username} and your password is {password}."
            )
        )

        self.textinput_username.text = ""
        self.textinput_password.text = ""

class app(App):
    def build(self):
        return MyGridLayout()
    
if __name__ == "__main__":
    app().run()