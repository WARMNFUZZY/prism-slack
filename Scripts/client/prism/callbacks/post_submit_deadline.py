# from Scripts.client.slack.slack_config import SlackConfig
# from Scripts.client.prism.api import API
# from Scripts.client.prism.utils.deadline_submission import deadline_submission_script
# from pprint import pprint
# import os
# import re
# import PrismCore


# def postSubmit_Deadline(core, origin, jobResult, jobInfos, pluginInfos, arguments):
#     deadline = core.getPlugin("Deadline")
#     config = SlackConfig(core).load_config(mode="studio")
#     state = getattr(core.getStateManager(), "curExecutedState", None)

#     pprint(f"Core: {core}")
#     pprint(f"Origin: {origin}")
#     pprint(f"JobResult: {jobResult}")
#     pprint(f"JobInfos: {jobInfos}")
#     pprint(f"PluginInfos: {pluginInfos}")
#     pprint(f"Arguments: {arguments}")

#     if state.chb_slackPublish.isChecked():
#         job = jobInfos.get("BatchName") or jobInfos.get("Name")
#         try:
#             output = jobInfos.get("OutputFilename0")
#             output = output.replace("\\", "/")
#         except:
#             output = None

#         if state.chb_mediaConversion.isChecked():
#             if output is not None:
#                 os.environ["JOB_OUTPUT_PATH"] = output
                
#             if "_mediaConversion" in job:
#                 id = re.search(r"JobID=([a-f0-9]+)", jobResult)
#                 if id:
#                     job_dependency = id.group(1)

#                 output = os.getenv("JOB_OUTPUT_PATH")
#                 job = job.replace("_mediaConversion", "")

#             else:
#                 return
#         else:
#             job_dependency = deadline.getJobIdFromSubmitResult(jobResult)
        
#         if "_updateMaster" in job:
#             return

#         if "_publishToSlack" in job:
#             return
        
#         prism_user = API(core).get_prism_slack_username()

#         state_data = {
#             "range_type": state.cb_rangeType.currentText(),
#             "publish_to_slack": state.chb_slackPublish.isChecked(),
#             "comments": state.te_comments.toPlainText(),
#             "state_type": "render",
#             "ui": "DL",
#             "convert_media": state.chb_mediaConversion.isChecked(),
#             "converted_extension": state.cb_mediaConversion.currentText().lower(),
#         }

#         if state.cb_rangeType.currentText() == "Custom":
#             state_data["start_frame"] = state.sp_rangeStart.text()
#             state_data["end_frame"] = state.sp_rangeEnd.text()
#         else:
#             state_data["start_frame"] = state.l_rangeStart.text()
#             state_data["end_frame"] = state.l_rangeEnd.text()

#         if config["slack"]["approvals"].get("enabled") == "True":
#             state_data["status"] = state.cb_status.currentText()
#         else:
#             state_data["status"] = None

#         code = deadline_submission_script(
#             core, output, state_data, prism_user
#         )

#         deadline.submitPythonJob(
#             code=code,
#             jobName=job + "_publishToSlack",
#             jobPrio=80,
#             jobPool=jobInfos.get("Pool"),
#             jobSndPool=jobInfos.get("SecondaryPool"),
#             jobGroup=jobInfos.get("Group"),
#             jobTimeOut=180,
#             jobMachineLimit=jobInfos.get("MachineLimit"),
#             frames="1",
#             suspended=jobInfos.get("InitialStatus") == "Suspended",
#             jobDependencies=[job_dependency],
#             args=arguments,
#             state=state,
#         )
    
#     else:
#         return