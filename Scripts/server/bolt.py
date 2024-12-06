import sys
from slack_bolt import App

from .events import SlackEvents

class SlackBoltServer():
    def __init__(self, core, token, app_token):
        self.core = core
        self.token = token

        # Initializes your app with your bot token
        app = App(token=self.token)

        events = SlackEvents(app, token)
        
        # Start your app
        if __name__ == "__main__":
            from slack_bolt.adapter.socket_mode import SocketModeHandler

            self.app_token = app_token
            SocketModeHandler(app, self.app_token).start()
