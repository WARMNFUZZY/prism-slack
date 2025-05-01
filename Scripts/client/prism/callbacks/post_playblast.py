from Scripts.client.prism.api import API
from Scripts.client.prism.utils.publish_to_slack import PublishToSlack


# Handle output result after playblast
def postPlayblast(core, **kwargs):
    state = kwargs.get("state", None)

    if hasattr(state, "gb_slack"):
        if state.gb_slack.isChecked():
            if state.chb_slackPublish.isChecked():
                output = kwargs.get("outputpath", None)
                output = output.replace("\\", "/")
                prism_user = API(core).get_prism_slack_username()

                state_data = {
                    "project": API(core).get_current_project(),
                    "range_type": state.cb_rangeType.currentText(),
                    "extension": state.cb_formats.currentText(),
                    "publish_to_slack": state.chb_slackPublish.isChecked(),
                    "comments": state.te_slackComments.toPlainText(),
                    "state_type": "pb",
                    "ui": "SM",
                    "app": core.appPlugin.pluginName,
                }

                if state.cb_rangeType.currentText() == "Custom":
                    state_data["start_frame"] = state.sp_rangeStart.text()
                    state_data["end_frame"] = state.sp_rangeEnd.text()
                else:
                    state_data["start_frame"] = state.l_rangeStart.text()
                    state_data["end_frame"] = state.l_rangeEnd.text()

                if core.getPlugin("MediaExtension"):
                    state_data["convert_media"] = state.chb_mediaConversion.isChecked()
                    state_data["converted_extension"] = (
                        state.cb_mediaConversion.currentText()
                    )
                else:
                    state_data["convert_media"] = None
                    state_data["converted_extension"] = None

                if core.getPlugin("Deadline"):
                    if hasattr(state, "gb_submit"):
                        if state.gb_submit.isChecked():
                            return
                        else:
                            PublishToSlack(core).publish_to_slack(output, state_data, prism_user)
                    else:
                        PublishToSlack(core).publish_to_slack(output, state_data, prism_user)
                else:
                    PublishToSlack(core).publish_to_slack(output, state_data, prism_user)

    return
