import os
import sys


def setupPaths():
    sys.path.append(os.getenv("BOLTPATH"))
    sys.path.append(os.getenv("SCRIPTSPATH"))
    sys.path.append(os.getenv("PRISMPATH"))
    sys.path.append(os.getenv('PRISM_CORE'))
    sys.path.append(os.getenv('PRISM_UTILS'))
    sys.path.append(os.getenv('PRISMPATH'))
    sys.path.extend(os.getenv("PATH").split(";"))


setupPaths()

from slack_bolt import App
import PrismCore
from server.events import SlackEvents


class SlackBoltServer:
    def __init__(self, token, app_token):
        self.token = token
        self.app_token = app_token
        self.app = App(token=self.token)

        pcore = PrismCore.create(prismArgs=["noUI"])

        # Initialize the Slack Events to be used in the Slack Bolt Server
        self.events = SlackEvents(self.app, token, core=pcore)


if __name__ == "__main__":
    from slack_bolt.adapter.socket_mode import SocketModeHandler

    # Start the Slack Bolt Server
    bolt = SlackBoltServer(sys.argv[1], sys.argv[2])
    SocketModeHandler(bolt.app, bolt.app_token).start()
