import os
import sys

def setupPaths():
    sys.path.append(os.getenv("BOLTPATH"))
    sys.path.append(os.getenv("SCRIPTSPATH"))
    sys.path.append(os.getenv("PRISMPATH"))
    sys.path.append(f'{os.getenv("PRISMPATH")}\..\..\Scripts')
    sys.path.extend(os.getenv("PATH").split(";"))

setupPaths()

from slack_bolt import App

from server.events import SlackEvents
from server.blocks import SlackBlocks

class SlackBoltServer():
    def __init__(self, token, app_token):
        self.token = token
        self.app_token = app_token
        self.app = App(token=self.token)

        self.blocks = SlackBlocks()

        self.events = SlackEvents(self.app, token, self.blocks)
        
        from pprint import pprint
        # pprint(sys.path)
if __name__ == "__main__":
    from slack_bolt.adapter.socket_mode import SocketModeHandler

    bolt = SlackBoltServer(sys.argv[1], sys.argv[2])
    SocketModeHandler(bolt.app, bolt.app_token).start()
