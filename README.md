# Wellbeing-Checker-V1
A desktop app made in python that:
  1. Summarizes your wellbeing throughout the month and ongoing, in the form of statistics and AI's opinion.
  2. Helps you recall your best and worst memories.

# Features in V1
  1. Accepts user input as a diary.
  2. A time limit of how much the app has been opened, for it to NOT be a distraction, because this app is made only for short diary inputs.
     - for example, the limit to open the app is 15 mins, beyond that the app is closed automatically and can't be opened until tomorrow's session.
     - you can technically open the app after the timer has finished, but you can't type anything (you can still log in / sign up).
     - when the timer is in 5 minutes, it will flash red and black.
  3. A setting page where you can set up your time limit for the app (30 minutes MAX).
  4. All diary inputs are stored in a local database (locally in your storage) so you can search your best and worst memories in the app.
  5. Currently, the app doesn't accept image or any other format, only TEXT is accepted.
  6. A greeting message to the user, which randomly rotates around the words:
     - "Have a nice day!"
     - "How's your day so far? Doing good?
     - "Hope you feeling good!"
     - "Best of luck for today!"
     - "Cheer up, will ya!"