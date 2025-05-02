# -----------
# Created by John Kesig while at Warm'n Fuzzy
# Contact: john.d.kesig@gmail.com

import os
import re
from functools import partial

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from Scripts.client.slack.slack_config import SlackConfig
from Scripts.client.prism.api import API
from Scripts.server.controls import ServerControls
from Scripts.client.prism.callbacks.media_player_context_menu_requested import (
    mediaPlayerContextMenuRequested,
)
from Scripts.client.prism.callbacks.on_state_startup import onStateStartup
from Scripts.client.prism.callbacks.post_playblast import postPlayblast
from Scripts.client.prism.callbacks.post_render import postRender
from Scripts.client.prism.callbacks.pre_render import preRender
from Scripts.client.prism.callbacks.pre_playblast import prePlayblast
from Scripts.client.prism.utils.deadline_submission import deadline_submission_script

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class Prism_Slack_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin
        self.config = SlackConfig(self.core)

        self.slack_config = self.config.load_config(mode="studio")
        self.config.check_slack_studio_options(self.slack_config)

        self.core.registerCallback(
            "mediaPlayerContextMenuRequested",
            partial(mediaPlayerContextMenuRequested, self.core),
            plugin=self.plugin, priority=30
        )
        self.core.registerCallback(
            "onStateStartup", partial(onStateStartup, self.core), plugin=self, priority=15
        )
        self.core.registerCallback(
            "postPlayblast", partial(postPlayblast, self.core), plugin=self, priority=15
        )
        self.core.registerCallback(
            "postRender", partial(postRender, self.core), plugin=self, priority=15
        )
        self.core.registerCallback(
            "preRender", partial(preRender, self.core), plugin=self, priority=15
        )
        self.core.registerCallback(
            "prePlayblast", partial(prePlayblast, self.core), plugin=self, priority=15
        )
        self.core.registerCallback(
            "postSubmit_Deadline", self.postSubmit_Deadline, plugin=self, priority=15
        )

    # Sets the plugin as active
    @err_catcher(name=__name__)
    def isActive(self):
        return True
    
    @err_catcher(name=__name__)
    def start_bolt_server(self):
        ServerControls(self.core).start_server()
    
    @err_catcher(name=__name__)
    def stop_bolt_server(self):
        ServerControls(self.core).stop_server()

    @err_catcher(name=__name__)
    def reset_bolt_server_status(self):
        ServerControls(self.core).reset_server_status()

    @err_catcher(name=__name__)
    def postSubmit_Deadline(self, origin, jobResult, jobInfos, pluginInfos, arguments):
        state = getattr(self.core.getStateManager(), "curExecutedState", None)
        if not state:
            return

        if state.gb_slack.isChecked():
            if state.chb_slackPublish.isChecked():
                job = jobInfos.get("Name")

                if state.cb_master.currentText() != "Don't Update Master":
                    batch = jobInfos.get("BatchName")
                else:
                    batch = ""

                try:
                    output = jobInfos.get("OutputFilename0")
                    output = output.replace("\\", "/")
                    if output is None:
                        return
                    
                except:
                    output = None

                exit_names = ["_updateMaster", "_publishToSlack", "_cleanup", "_export"]
                
                for name in exit_names:
                    if name in jobInfos.get("Name"):
                        return

                if self.core.getPlugin("MediaExtension") is not None:
                    if hasattr(state, "chb_mediaConversion"):
                        if state.chb_mediaConversion.isChecked():
                            if output is not None:
                                os.environ["JOB_OUTPUT_PATH"] = output
                                
                            if "_mediaConversion" in jobInfos.get("Name"):
                                id = re.search(r"JobID=([a-f0-9]+)", jobResult)
                                if id:
                                    job_dependency = id.group(1)
                                
                                output = os.getenv("JOB_OUTPUT_PATH")
                                job = job.replace("_mediaConversion", "")
                                
                            else:
                                return
                        else:
                            job_dependency = self.core.getPlugin("Deadline").getJobIdFromSubmitResult(jobResult)
                    else:
                        job_dependency = self.core.getPlugin("Deadline").getJobIdFromSubmitResult(jobResult)
                else:
                    job_dependency = self.core.getPlugin("Deadline").getJobIdFromSubmitResult(jobResult)
                
                prism_user = API(self.core).get_prism_slack_username()

                state_data = {
                    "project": API(self.core).get_current_project(),
                    "range_type": state.cb_rangeType.currentText(),
                    "publish_to_slack": state.chb_slackPublish.isChecked(),
                    "comments": state.te_slackComments.toPlainText(),
                    "state_type": "render",
                    "ui": "DL",
                    "app": self.core.appPlugin.pluginName,
                }

                if state.cb_rangeType.currentText() == "Custom":
                    state_data["start_frame"] = state.sp_rangeStart.text()
                    state_data["end_frame"] = state.sp_rangeEnd.text()
                
                else:
                    state_data["start_frame"] = state.l_rangeStart.text()
                    state_data["end_frame"] = state.l_rangeEnd.text()

                if self.core.getPlugin("MediaExtension") is not None:
                    state_data["convert_media"] = state.chb_mediaConversion.isChecked()
                    state_data["converted_extension"] = (
                        state.cb_mediaConversion.currentText().lower()
                    )
                else:
                    state_data["convert_media"] = None
                    state_data["converted_extension"] = None

                code = deadline_submission_script(
                    self.core, output, state_data, prism_user
                )

                dl = self.core.getPlugin("Deadline")

                result = dl.submitPythonJob(
                    code=code,
                    jobName=job + "_publishToSlack",
                    jobPrio=80,
                    jobPool=jobInfos.get("Pool"),
                    jobSndPool=jobInfos.get("SecondaryPool"),
                    jobGroup=jobInfos.get("Group"),
                    jobTimeOut=180,
                    jobMachineLimit=jobInfos.get("MachineLimit"),
                    frames="1",
                    suspended=jobInfos.get("InitialStatus") == "Suspended",
                    jobDependencies=[job_dependency],
                    jobBatchName=batch,
                    args=arguments,
                    state=state,
                )

        return