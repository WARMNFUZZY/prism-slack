#-----------
# Created by John Kesig while at Warm'n Fuzzy
# Contact: john.d.kesig@gmail.com

import os
import requests
import subprocess
import glob
import re
import json

from pathlib import Path

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

#REMOVE THIS IMPORT LINE BEFORE PUBLISH. ONLY DESIGNED TO REMOVE THE PROBLEMS UNDER THE CLASSES
# from PyQt6 import QtWidgets, QGroupBox, QVBoxLayout, QCheckBox, QComboBox, QLabel, QSpinBox, QFileDialog, QInputDialog, QMessageBox, QAction, QDialog, QTimer
from server.blocks import SlackBlocks

from integration.slack_config import SlackConfig
from integration.user_pools import UserPools
from integration.slack_api import *

from util.dialogs import *
from util.state_manager_ui import StateManagerUI
from util.convert_image_sequence import ConvertImageSequence

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

# Publish content to Slack
class Prism_Slack_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        self.slack_config = SlackConfig(self.core)
        self.slack_user_pools = UserPools(self.core)
        self.slack_upload = UploadContent(self.core)
        self.slack_message = PostMessage(self.core)
        self.slack_user_info = UserInfo(self.core)
        self.slack_blocks = SlackBlocks()
        self.convert_image_sequence = ConvertImageSequence(self.core)

        self.core.registerCallback("mediaPlayerContextMenuRequested", self.mediaPlayerContextMenuRequested, plugin=self)
        self.core.registerCallback("onStateStartup", self.onStateStartup, plugin=self)
        self.core.registerCallback("postPlayblast", self.postPlayblast, plugin=self)
        self.core.registerCallback("postRender", self.postRender, plugin=self)
        self.core.registerCallback("preRender", self.preRender, plugin=self)

    @err_catcher(name=__name__)
    def onStateStartup(self, state):
        # Add Slack publishing options to the State Manager
        if state.className == "Playblast":
            lo = state.gb_playblast.layout()
        elif state.className == "ImageRender":
            lo = state.gb_imageRender.layout() 
        else:
            return

        if not hasattr(state, 'gb_slack'):
            state.gb_slack = QGroupBox()
            state.gb_slack.setTitle("Slack")
            state.gb_slack.setCheckable(True)
            state.gb_slack.setChecked(False)
            state.gb_slack.setObjectName("gb_slack")
            state.gb_slack.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            self.lo_slack_group = QVBoxLayout()
            self.lo_slack_group.setContentsMargins(-1, 15, -1, -1)
            state.gb_slack.setLayout(self.lo_slack_group)
            
            lo.addWidget(state.gb_slack)

        state.gb_slack.toggled.connect(lambda toggled: self.createSlackSubmenu(toggled, state))
    
    # Handle output result after playblast
    @err_catcher(name=__name__) 
    def postPlayblast(self, **kwargs):
        global state 
        state = kwargs.get('state', None)

        if state.gb_slack.isChecked():
            if state.chb_slackPublish.isChecked():
                print("Slack Pubish: Checked")
                print(kwargs.get("settings", None))
                outputPath = kwargs.get("settings", None)['outputName']
                ext = os.path.splitext(outputPath)[1].replace(".", "")

                rangeType = state.cb_rangeType.currentText()

                if rangeType == "Single Frame" or rangeType in ['Scene', 'Shot']:
                    startFrame = state.l_rangeStart.text()
                    endFrame = state.l_rangeEnd.text()

                if rangeType == "Custom":
                    startFrame = state.sp_rangeStart.text()
                    endFrame = state.sp_rangeEnd.text()
                
                if rangeType == "Expression":
                    self.core.popup("Your render has been published but the Slack plugin does not support expression ranges yet.")
                    return

                if ext in ['.png', '.jpg']:
                    if rangeType == "Single Frame":
                        outputList = [outputPath]
                    
                    if rangeType != "Single Frame" and startFrame == endFrame:
                        file = outputPath.replace("#" * self.core.framePadding, str(startFrame))
                        outputList = [file]

                    if rangeType != "Single Frame" and startFrame < endFrame:                    
                        if state.chb_mediaConversion.isChecked() is False:
                            convert = self.convert_image_sequence.convertImageSequence(outputPath)
                            outputList = [convert]
                    
                    if state.chb_mediaConversion.isChecked() is True:
                        option = state.cb_mediaConversion.currentText().lower()

                        base = os.path.basename(outputPath).split(".")[0]
                        top_directory = os.path.dirname(outputPath)

                        converted_directory = f"{top_directory} ({ext})"
                        converted_file = f"{converted_directory}/{base} ({ext}).{ext}"
                        outputList = [converted_file]

                        if option in ['png', 'jpg']:
                            framePad = '#' * self.core.framePadding
                            sequence = f"{converted_directory}/{base} ({ext}).{framePad}.{ext}"
                            convert = self.convert_image_sequence.convertImageSequence(sequence)
                            outputList = [convert]

                self.publishToSlack_fromSM(outputList)

        return

    @err_catcher(name=__name__)
    def preRender(self, **kwargs):
        global state 
        state = kwargs.get('state', None)

        access_token = self.getAccessToken()
        if state.gb_slack.isChecked():
            if state.chb_slackNotify.isChecked():
                notify_user = state.cb_userPool.currentText()
                project = self.getCurrentProject()
                channel = self.getChannelId(access_token, project)
                channel_users = self.slack_user_pools.getChannelUsers(access_token, channel)
                notify_user_id = self.getSlackUserId(notify_user, channel_users)
                product = state.l_taskName.text()
                sender_id = self.getSlackUserId(self.getPrismSlackUsername(), channel_users)
                
                self.notifySlackUser(access_token, notify_user_id, channel, product, sender_id)

    # Handle the output result after rendering
    @err_catcher(name=__name__)
    def postRender(self, **kwargs):
        global state 
        state = kwargs.get('state', None)
        
        if state.gb_slack.isChecked():
            if state.chb_slackPublish.isChecked():
                outputPath = kwargs.get("settings", None)["outputName"]
                ext = os.path.splitext(outputPath)[1].replace(".", "")

                rangeType = state.cb_rangeType.currentText()

                if rangeType == "Single Frame" or rangeType in ['Scene', 'Shot']:
                    startFrame = state.l_rangeStart.text()
                    endFrame = state.l_rangeEnd.text()

                if rangeType == "Custom":
                    startFrame = state.sp_rangeStart.text()
                    endFrame = state.sp_rangeEnd.text()
                
                if rangeType == "Expression":
                    self.core.popup("Your render has been published but the Slack plugin does not support expression ranges yet.")
                    return

                if ext in ['exr', 'png', 'jpg']:
                    if rangeType == "Single Frame":
                        outputList = [outputPath]

                    if rangeType != "Single Frame" and startFrame == endFrame:
                        file = outputPath.replace("#" * self.core.framePadding, str(startFrame))
                        outputList = [file]

                    if rangeType != "Single Frame" and startFrame < endFrame:                 
                        if state.chb_mediaConversion.isChecked() is False:
                            convert = self.convert_image_sequence.convertImageSequence(outputPath)
                            outputList = [convert]
                        else:
                            option = state.cb_mediaConversion.currentText().lower()
                            ext = self.retrieveExtension(option)

                            base = os.path.basename(outputPath).split(".")[0]
                            version_directory = os.path.dirname(os.path.dirname(outputPath))
                            aov_directory = os.path.basename(os.path.dirname(outputPath))
                            file = base.split(f'_{aov_directory}')[0]

                            converted_directory = f"{version_directory} ({ext})/{aov_directory}"
                            converted_files = f"{converted_directory}/{file} ({ext})_{aov_directory}.{ext}"
                            
                            outputList = [converted_files]

                            if ext in ['png', 'jpg']:
                                framePad = '#' * self.core.framePadding
                                sequence = f"{converted_directory}/{file} ({ext})_{aov_directory}.{framePad}.{ext}"
                                convert = self.convert_image_sequence.convertImageSequence(sequence)
                                outputList = [convert]
                                
                self.publishToSlack_fromSM(outputList)
        
        return
    
    # Sets the plugin as active
    @err_catcher(name=__name__)
    def isActive(self):
        return True
  
    # Get current version in the Media tab in the Prism Project Browser   
    @err_catcher(name=__name__)
    def mediaPlayerContextMenuRequested(self, origin, menu):    
        if not type(origin.origin).__name__ == "MediaBrowser":   
            return   

        self.identifier = origin.origin.getCurrentIdentifier()['identifier']     
        self.sequence = origin.origin.getCurrentIdentifier()['sequence']   
        self.shot = origin.origin.getCurrentIdentifier()['shot'] 
        self.version = origin.origin.getCurrentVersion()['version']

        action = QAction("Publish to Slack", origin)
        iconPath = os.path.join(self.pluginDirectory, "Resources", "slack-icon.png")
        icon = self.core.media.getColoredIcon(iconPath)
        
        action.triggered.connect(lambda: self.publishToSlack_fromMedia(
            origin.seq, 
            self.identifier, 
            self.sequence, 
            self.shot, 
            self.version))
        
        menu.insertAction(menu.actions()[-1], action)
        action.setIcon(icon)

    @err_catcher(name=__name__)
    def createSlackSubmenu(self, toggled, state):
        self.state_manager_ui = StateManagerUI(self.core)
        # If the group box is toggled on
        if toggled:
            if not hasattr(state, 'cb_userPool'):
                self.state_manager_ui.createStateManagerSlackUI(state)

                self.populateUserPool(state)

        else:
            layout = state.gb_slack.layout()
            self.state_manager_ui.removeCleanupLayout(layout, 'lo_slack_publish', state)
            self.state_manager_ui.removeCleanupLayout(layout, 'lo_slack_notify', state)

    @err_catcher(name=__name__)
    def populateUserPool(self, state):
        access_token = self.getAccessToken()
        proj = self.getCurrentProject()
        channel_id = self.getChannelId(access_token, proj)

        notify_user_pool = self.getNotifyUserPool().lower()
        users = []
        if notify_user_pool == "studio":
            users = self.slack_user_pools.getStudioUsers(state)
        
        elif notify_user_pool == "channel":
            members = self.slack_user_pools.getChannelUsers(access_token, channel_id)
            users = [member['display_name'] for member in members]
        
        elif notify_user_pool == "team":
            members = self.slack_user_pools.getTeamUsers(access_token)
            users = [member['display_name'] for member in members]

        state.cb_userPool.addItems(users)

    # remove widgets and cleanup sub-layouts when the group box is toggled off
    @err_catcher(name=__name__)
    def removeCleanupLayout(self,layout, attribute_name, state):
        if hasattr(state, attribute_name):
            sub_layout = getattr(state, attribute_name)
            if sub_layout:
                for i in reversed(range(sub_layout.count())):
                    item = sub_layout.itemAt(i)
                    if item.widget(): 
                        widget = item.widget()
                        sub_layout.removeWidget(widget)
                        widget.deleteLater()

                layout.removeItem(sub_layout)
                sub_layout.deleteLater()

                delattr(state, attribute_name)

    # Get proper extension from media conversion type
    @err_catcher(name=__name__)
    def retrieveExtension(self, option):
        if 'png' in option:
            ext = 'png'
        elif 'jpg' in option:
            ext = 'jpg'
        elif 'mp4' in option:
            ext ='mp4'
        elif 'mov' in option:
            ext ='mov'
        else:
            ext = option
        
        return ext
    
    # Convert image sequence to MP4 for Slack
    # @err_catcher(name=__name__)
    # def convertImageSequence(self, sequence):
    #     # Define the "slack" output folder
    #     folder_path = os.path.dirname(sequence)
    #     slack_folder = os.path.join(folder_path, "slack")
        
    #     if not os.path.exists(slack_folder):
    #         os.makedirs(slack_folder)

    #     # Construct input and output paths
    #     input_sequence = sequence.replace('.####.', '.%04d.')
    #     basename = os.path.basename(sequence).split('.####.')[0]
    #     output_file = os.path.join(slack_folder, basename + '.mp4')
        
    #     ffmpegPath = os.path.join(self.core.prismLibs, "Tools", "FFmpeg", "bin", "ffmpeg.exe")
    #     ffmpegPath = ffmpegPath.replace('\\', '/')

    #     if not os.path.exists(ffmpegPath):
    #         self.core.popup(f"ffmpeg not found at {ffmpegPath}")
    #         return

    #     # Search for matching files to determine the start frame
    #     pattern = sequence.replace('.####.', '.*.')
    #     files = sorted(glob.glob(pattern))
    #     if not files:
    #         self.core.popup(f"No files found matching pattern: {pattern}")
    #         return
        
    #     start_frame = re.search(r"\.(\d{4})\.", files[0])
    #     if start_frame:
    #         start_frame = start_frame.group(1)
    #     else:
    #         self.core.popup("Failed to determine the starting frame.")
    #         return

    #     # Run ffmpeg to create the video
    #     try:
    #         result = subprocess.run([
    #             ffmpegPath,
    #             "-framerate", "24",
    #             "-start_number", start_frame,
    #             "-i", input_sequence,
    #             "-c:v", "libx264",
    #             "-pix_fmt", "yuv420p",
    #             output_file
    #         ], capture_output=True, check=True)
    #     except subprocess.CalledProcessError as e:
    #         self.core.popup(f"Error running ffmpeg: {e.stderr.decode()}")
    #         return

    #     output_file = output_file.replace("\\", "/")
    #     return output_file

    # @err_catcher(name=__name__)
    # def getSlackConfig(self):
    #     if self.isStudioLoaded() is None:
    #         prjConfig_path = os.path.dirname(self.core.prismIni)
    #         config = os.path.join(prjConfig_path, "pipeline.json")
    #     else:
    #         studio_plugin = self.core.getPlugin('Studio')
    #         config = os.path.join(studio_plugin.getStudioPath(), "configs", "slack.json")

    #     return config
    
    @err_catcher(name=__name__)
    def getNotifyUserPool(self):
        slack_config = self.slack_config.loadConfig("studio")
            
        return slack_config["slack"]['notifications'].get('user_pool')
    
    @err_catcher(name=__name__)
    def getNotifyUserMethod(self):
        slack_config = self.slack_config.loadConfig("studio")
            
        return slack_config["slack"]['notifications'].get('method')

    # Get Slack Access Token from environment variable
    @err_catcher(name=__name__)
    def getAccessToken(self):
        slack_config = self.slack_config.loadConfig("studio")
            
        return slack_config["slack"]["token"]

    # Get Slack Channel ID from conversation list
    @err_catcher(name=__name__)
    def getChannelId(self, access_token, project_name):
        conversation_id = None

        try:
            url = "https://slack.com/api/conversations.list"
            headers = {
                "Authorization": f"Bearer {access_token}"
                }
            response = requests.get(url, headers=headers)

            conversations = response.json()

            for conversation in conversations["channels"]:
                if conversation["name"] == project_name:
                    conversation_id = conversation["id"]
                    return conversation_id

        except:
            print("Failed to retrieve conversation members.")
            return None
    
    # Get Slack Display Name from prism user configuration
    @err_catcher(name=__name__)
    def getPrismSlackUsername(self):
        user_data = self.slack_config.loadConfig("user")

        return user_data["slack"].get("username")

    # Get Slack User ID from user list
    @err_catcher(name=__name__)
    def getSlackUserId(self, username, user_pool):
        for user in user_pool:
            print(user)
            if username == user['display_name']:
                return user.get('id')

        return None

    @err_catcher(name=__name__)
    def teamsUserWarning(self, user):
        dialog = WarningDialog(team_user=user)
        if dialog.exec_() == QDialog.Accepted:
            return True
        else:
            return False

    # Notify user about new version of product is on the way!
    @err_catcher(name=__name__)
    def notifySlackUser(self, access_token, slack_user, channel, product, sender):
        if os.getenv('PRISM_SEQUENCE') is not None:
            seq = os.getenv('PRISM_SEQUENCE')
            shot = os.getenv('PRISM_SHOT')

        message = self.getMessage(slack_user, seq, shot, product, sender)

        self.slack_message.postChannelMessage(access_token, channel, message)

    @err_catcher(name=__name__)
    def getMessage(self, slack_user, seq, shot, product, sender):
        import random
        if random.randint(0, 100) == 90:
            message = f"Dearest <@{slack_user}>,\nI bring you tidings of the utmost importance! The {product} render for Shot `{shot}` in the enchanting Sequence `{seq}` has begun. Courtesy of the illustrious <@{sender}>, of course. May the pixels align in harmonious perfection!\nYours in cinematic anticipation,\nMoira Rose"

        elif random.randint(0, 100) == 100:
            message = f"<@{slack_user}>\n`{product}`/`{seq}`/`{shot}`\n<https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExeW4xNGl1dGxtMWY5d2tsMTBuYXc3enYza3FkNnpoZDNoYWlremh5NSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/SSiwN19NtD1xUAikqf/giphy.gif>"

        elif state.cb_userPool.currentText() == "dwalz" and random.randint(0, 100) == 80:
            message = f"<@{slack_user}>! Ew, David! Okay, like, I just had to tell you—{product} for Shot `{shot}` in Sequence {seq} is, like, officially rendering. It’s going to be so fabulous, like, total gallery-wall vibes. Don’t mess this up, okay bye!"

        else:
            message = f"Heads up <@{slack_user}>!\n A new version of `{product}` for `{seq}`/`{shot}` is on the way!"

        return message

    @err_catcher(name=__name__)
    def getCurrentProject(self):
        proj = self.core.getConfig("globals", "project_name", configPath=self.core.prismIni).lower()

        return proj
    
    # Upload file to Slack
    @err_catcher(name=__name__)
    def uploadToSlack(self, access_token, conversation_id, file_upload, sequence, shot, identifier, version, method):
        import time
        prism_user = self.getPrismSlackUsername()
        channel_users = self.slack_user_pools.getChannelUsers(access_token, conversation_id)
        slack_user = self.getSlackUserId(prism_user, channel_users)

        user_avatar = self.slack_user_info.getUserAvatar(access_token, slack_user)
        
        # Set additional comments for the upload
        info_dialog = AdditionalInfoDialog()
        if info_dialog.exec_() == QDialog.Accepted:
            comment = info_dialog.get_comments()
            status = info_dialog.get_status()
        else:
            self.upload_message.close()
            return
        
        try: 
            # Upload the file to Slack
            self.upload = self.slack_upload.uploadContent(access_token, conversation_id, file_upload)
            
            # Wait for 2s before posting the message (this is due to the fact that Slack could take a while to process the file)
            time.sleep(2)
            
            # Post the message to the channel
            self.slack_message.postProgressMessage(access_token, conversation_id, sequence, shot, identifier, version, slack_user, user_avatar, comment, status)

            # Post the successful upload message
            uploaded = True
            SuccessfulPOST(uploaded, method, self.upload_message)
            
        except Exception as e:
            uploaded = False
            print(f"Failed to upload file to Slack: {e}")
            SuccessfulPOST(uploaded, method, self.upload_message)

    # Publish file to Slack
    @err_catcher(name=__name__)
    def publishToSlack_fromMedia(self, file, identifier, sequence, shot, version):
        current_project = self.core.getConfig("globals", "project_name", configPath=self.core.prismIni).lower()
        
        access_token = self.getAccessToken()
        conversation_id = self.getChannelId(access_token, current_project)

        file_upload = file[0]
        file_upload.replace("\\", "/")

        self.upload_message = UploadDialog()
        self.upload_message.show()

        QTimer.singleShot(0, lambda: self.uploadToSlack(access_token, conversation_id, file_upload, sequence, shot, identifier, version, method="Media"))

    @err_catcher(name=__name__)
    def publishToSlack_fromSM(self, file):
        current_project = self.core.getConfig("globals", "project_name", configPath=self.core.prismIni).lower()
        
        access_token = self.getAccessToken()
        conversation_id = self.getChannelId(access_token, current_project)
        file_upload = file[0]
        file_upload.replace("\\", "/")

        self.upload_message = UploadDialog()
        self.upload_message.show()

        QTimer.singleShot(0, lambda: self.uploadToSlack(access_token, conversation_id, file_upload, method="SM" ))

    # def successfulPOST(self, uploaded, method):
    #     self.upload_message.close()

    #     if uploaded == True and method == "Media":
    #         QMessageBox.information(None, "Slack Upload", "Asset has been uploaded successfully")
    #     elif uploaded == False:
    #         QMessageBox.warning(None, "Slack Upload", "Failed to upload asset to Slack")
    #     else:
    #         None        

    @err_catcher(__name__)
    def isStudioLoaded(self):
        studio = self.core.plugins.getPlugin("Studio")
        return studio