import os

from Scripts.client.prism.ui import UploadDialog, SuccessfulPOST
from Scripts.client.prism.api import API
from Scripts.client import slack
from Scripts.client.prism.utils.convert_image_sequence import check_conversion

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

class PublishToSlack:
    def __init__(self, core):
        self.core = core

    def publish_to_slack(self, file, state_data, prism_user):
        if state_data["ui"] != "Media":
            ext = os.path.splitext(file)[1].replace(".", "")
            upload = check_conversion(self.core, state_data, ext, file)[0]
        else:
            upload = file[0]

        try:
            access_token = API(self.core).get_access_token()

        except Exception as e:
            raise (
                f"Failed to retrieve Slack access token. Please check your configuration.\n\n{e}"
            )

        try:
            upload.replace("\\", "/")
        except Exception as e:
            print("")
        
        if state_data["ui"] != "DL":
            QTimer.singleShot(
                0,
                lambda: self.upload_to_slack(
                    access_token=access_token,
                    file=upload,
                    state_data=state_data,
                    prism_user=prism_user
                ),
            )
        else:
            self.upload_to_slack(
                access_token=access_token,
                file=upload,
                state_data=state_data,
                prism_user=prism_user
            )
        

    # Upload file to Slack
    def upload_to_slack(self, access_token, file, state_data, prism_user):
        if state_data["ui"] == "Media":
            upload_dialog = UploadDialog()
            upload_dialog.show()

        current_project = f"{state_data['project']}"
        channel_id = slack.get_channel_id(access_token, current_project)
        channel_users = slack.get_channel_users(access_token, channel_id)
        slack_user = API(self.core).get_slack_user_id(prism_user, channel_users)

        comment = state_data["comments"]

        try:
            # Upload the file to Slack
            upload = slack.upload_content(access_token, channel_id, file, slack_user, comment)

            # Post the successful upload message
            uploaded = True
            if state_data["ui"] == "Media":
                upload_dialog.close()
                SuccessfulPOST(uploaded, state_data["ui"])

        except Exception as e:
            uploaded = False
            print(f"Failed to upload file to Slack: {e}")
            if state_data["ui"] == "Media":
                SuccessfulPOST(uploaded, state_data["ui"])
