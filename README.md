<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/WARMNFUZZY/prism-slack/blob/main/Resources/prism_slack_logo_long_light_banner.png">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/WARMNFUZZY/prism-slack/blob/main/Resources/prism_slack_logo_long_dark_banner.png">
  <img alt="Prism and Slack branding" src="https://github.com/WARMNFUZZY/prism-slack/tree/main/Resources/prism_slack_logo_long_light_banner.png">
</picture>  
  
<div>
<img src="https://img.shields.io/badge/Prism_Pipeline-2.0.16-mediumseagreen" alt="Prism Pipeline Version"> 
<img src="https://img.shields.io/badge/Slack_Plugin-2.0.16-4A154B?logo=slack" alt="Slack Plugin Version">
</div>  
<br>
  
> [!IMPORTANT]  
> Most up to date docs can be found here: [Warm'n Fuzzy Slack Plugin Documentation](https://coda.io/@wf-jkesig/warmn-fuzzy-slack-plugin)
  
    
## Table of Contents  
1. [Introduction](#introduction)
2. [Requirements](#requirements)
    1. [Slack](#requirements-slack)
3. [Installation](#installation)
    1. [Prism - Install Plugin](#plugin)

## Introduction

This is the Slack plugin for Prism-Pipeline 2.0

## Requirements

### Slack

1. Slack Bot

   - You are required to create a bot application in Slack. You can find the installation process for this below or check the documentation here: [Slack Bot Installation](https://coda.io/@wf-jkesig/warmn-fuzzy-slack-plugin/installation-3)

2. Channel Name = Project Name
   - Your channel must match the name of your current project. If it doesn't, you will need to put it in the Custom Channel field in the project settings

## Installation

### CLI

For a shorter method of install the plugin, see the two commands below. Open a Terminal in your Prism Plugin directory and copy/paste/type in these commands:

> git clone https://github.com/WARMNFUZZY/prism-slack.git Slack

    pip install -r requirements.txt -t ./PythonLibs

### Plugin

If you want to avoid the next 4 steps below, you can open a terminal in the Prism Plugins directory and run this command

> git clone https://github.com/WARMNFUZZY/prism-slack.git Slack

1. Download the Plugin

> Option 1: Download the current release package from the repository's release page.

    Option 2: Download the repository as a ZIP file using the Code dropdown menu on the main repository page.

2.Unzip the File (if needed)

> If you downloaded the ZIP file, extract its contents to a folder.

3.  Move the Plugin to the Prism Plugin Folder

    > Locate your Prism Plugin folder.

        Drag and drop the downloaded or unzipped plugin folder into the Prism Plugin folder.

4.  Reload Prism

> Restart or reload Prism.

    The Slack plugin should automatically appear in the plugin list and be checked as enabled.

### Slack

We did not include the Slack API’s in the repository to limit the size of it. You can either download the release package or you can download it on your own. If you chose to download it on your own, please follow the steps below to do so.

If you want to avoid all of these steps below, you can open a terminal in the Slack plugin directory and run this command

> pip install -r requirements.txt -t ./PythonLibs

1. Install the Slack Bolt and Slack SDK
   > pip install slack_sdk

> pip install slack_bolt

2. Locate Slack API packages  
   If you do not know where to find the packages you just installed, run this command
   > pip show slack_sdk

> pip show slack_bolt

3. Copy/move them to this folder  
   If the PythonLibs folder does not exist, create it
   > {PRISM_PLUGIN_DIRECTORY}/Slack/PythonLibs
