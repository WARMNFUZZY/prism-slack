<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/animationem/prism-slack/blob/main/Resources/prism_slack_logo_long_light_banner.png">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/animationem/prism-slack/blob/main/Resources/prism_slack_logo_long_dark_banner.png">
  <img alt="Prism and Slack branding" src="https://github.com/animationem/prism-slack/blob/main/Resources/prism_slack_logo_long_light_banner.png">
</picture>  
  
<div>
<img src="https://img.shields.io/badge/Prism_Pipeline-2.0.13-mediumseagreen" alt="Prism Pipeline Version"> 
<img src="https://img.shields.io/badge/Slack_Plugin-2.0.13-4A154B?logo=slack" alt="Slack Plugin Version">
</div>
  
> [!IMPORTANT]  
> As this readme continues to grow, full docs will be migrated to a designated location that will be provided in the near future.  
  
> [!WARNING]
> This plugin is going to be getting reorganized for modularity. It is getting too big to only be primarily 2 files. Major updates are planned.  
  
    
## Table of Contents  
1. [Introduction](#introduction)
2. [Requirements](#requirements)
    1. [Prism](#requirements-prism)
    2. [Slack](#requirements-slack)
3. [Installation](#installation)
    1. [Prism - Install Plugin](#plugin)
    2. [Slack - Install Slack Bot](#slack-bot)
4. [Plugin Options](#plugin-options)
5. [Planned Features](#planned-features)
6. [Admins](#admins)
7. [Known Bugs/Limitations](#known-bugs-and-limitations)
8. [Devs](#devs)  


## Introduction
This is the Slack plugin for Prism-Pipeline 2.0  


## Requirements
### Prism  
Currently the Slack plugin uses your Real Name to cross compare the Prism User and the Slack User. Your Prism username needs to be set to your first initial along with your last name. As an example my username in Prism is: jkesig. It will compare this username with my Real Name on Slack: John Kesig. It will find my user id information and publish a message, while tagging me, to the channel.

This will be fixed with the option to allow for the users input, as this was a leftover feature from the studios internal version of this plugin. Once it is updated, this readme will reflect it.
  
### Slack  
1. Slack Bot
    - You are required to create a bot application in Slack. You can find the installation process for this below.

2. Your Name
    - You are also required to input your Real Name in your Slack profile. Your display name can be something different, but your Name must be input for proper tagging.

3. Channel Name = Project Name
    - Your channel must match the name of your current project. Will add the option for a [custom slack channel](#custom-slack-channel) in the future
  

## Installation
### Plugin
1. Download the Plugin  

>   Option 1: Download the current release package from the repository's release page.  
    Option 2: Download the repository as a ZIP file using the Code dropdown menu on the main repository page.

2.Unzip the File (if needed)
>   If you downloaded a ZIP file, extract its contents to a folder.

3. Move the Plugin to the Prism Plugin Folder
>   Locate your Prism Plugin folder.
    Drag and drop the downloaded or unzipped plugin folder into the Prism Plugin folder.

4. Reload Prism

>   Restart or reload Prism.  
    The Slack plugin should automatically appear in the plugin list and be checked as enabled.

### Slack Bot
1. Use the Provided Manifest

>    Locate the file [manifest.yml](Resources/manifest.yml) in the Resources folder of the repository. This file simplifies the bot creation process.

2. Create Your Slack App

>    Go to the [Your Apps](https://api.slack.com/apps/) page on the Slack API website.
    Follow the instructions for creating apps using manifests provided on this page: [Creating Apps using manifests](https://api.slack.com/reference/manifests#creating_apps).  
    Use the [manifest.yml](Resources/manifest.yml) file during the app creation process.

3. Customize the App Icon (Optional)

>    Once your app is created, navigate to the Basic Information page in the Slack API dashboard.  
    Under the Display Information section, upload an App Icon to personalize your app.

4. Install the App

>    In the left-hand menu, select the Install App section.  
    Install the app into your Slack workspace.

5. Obtain the Bot User OAuth Token

>    Go to the OAuth & Permissions page in the left-hand menu.  
    Copy the **Bot User OAuth Token** displayed on this page.

6. Enter the Token in Prism Settings

>    Open the Slack Project/Studio Settings page in Prism.
    Paste the copied Bot User OAuth token into the appropriate field to complete the integration.


## Plugin Options  
### Publish to Slack  
Currently there are two options that would allow you to publish you renders/playblasts directly to Slack. You can either do it via the Project Browser in the Media tab, or by sending it straight to Slack from the State Manager. 
<details>
    <summary>Project Browser</summary>

</details>

<details> 
    <summary>State Manager</summary>

</details>


### Notify Artist/User  


## Admins  
<details>
    <summary>Where is the Access Token stored?</summary>  

### Prism Plus/Pro with Studio Enabled
> {PRISM_STUDIO_PATH}\configs\slack.json  
### Open Source
> {PRISM_PROJECT_PATH}\00_Pipeline\pipeline.json
</details>

<details>
<summary>Notify Users Pool</summary>

### Studio  
This pool of artists will be drawn from the Prism Studio plugin. By default, it accepts all default user roles in the pool with the exception of users with the role: *Deactivated*

### Channel
This pool will be drawn from the list of users currently in the Slack Project Channel

### Team
This was taken out in favor of larger plans. I plan to include some options for Usergroups with the Teams option, but it will take time.
</details>


## Planned Features  

<details>
    <summary>Comments Based on Threads</summary>
    I will be including the option to include comments in threads on Slack as comments on Prism versions in the media tab.
</details>

<details>
    <summary>Version Status Actions</summary>
    I will be including some Actionable buttons below a publish to choose the current status once it's reviewed
</details>

<details>
    <summary><a name="custom-slack-channel">Custom Slack Channel Names</a></summary>
    I will give you the option to add custom slack channel names. Default option will still be the name of the project
</details>

<details>
    <summary>Reintroduce Teams User Pool</summary>
    There is already some code in the plugin that would enable you to load the entire team into the user pool. However it's kinda not a safe option. When I start working in Multi-Channel stuff for notifications, that is when I will reintroduce the Teams option for user pools.
</details>

<details>
    <summary>Multi-Channel Settings</summary>
    There has been some discussion around channels that are more suited for different department. This can also reduce the flood of notifications from larger projects.
</details>

<details>
    <summary>Include Usergroups for Team selection</summary>
    This is going to be part of a larger goal. Essentially you could create user groups based on department names, or something similar, and assign certain tasks to be part of certain user pools. This would be incoroporated with the Multi-Channel settings mentioned above.
</details>

<details>
    <summary>User Chosen Names</summary>
    I'll be adding a feature that will let the user choose their name according to their name on Slack in the Prism User Settings
</details>

<details>
    <summary>Notify via Ephemeral Messages</summary>
    Lots of messages could potentially flood the channel unncessarily to alert another artist of an incoming update. Ephemeral messages can help to reduce the impact.
</details>

<details>
    <summary>Notify via Direct Messages</summary>
    Direct messages to individual artists can bebe chosen as an option in order to avoid flooding the channel unneccesarily.
</details>


## Known Bugs and Limitations  
<details>
    <summary>Deadline Unsupported</summary>
    Currently publishing to the farm is unsupported. It will need a separate Python task as part of the job in order to carry out the publishing via render farm.
</details>

## Devs
List of all available functions accessible to the dev/user, what arguments they take, and what they accomplish on top of all of the available options Prism already provides.

|  Function        |  Arguments     |  Description  |
|  --------------  |  ------------  |  -----------  |
|  getAccessToken  |  No Arguments  |  Retrieve the access token from the slack json file.
|  getCurrentProject  |  No Arguemnets | Retrieve the current active project
|  getChannelId  |  {access_token},  {current_project}  |  Grabs the ID of the channel based on the current project
|  getPrismUser  |  No Arguments  |  Get the current prism instance user
|  getSlackUser  |  {access_token}, {user_pool}  |  Grab the ID of the slack user 
|  getStudioUsers  |  No Arguments  |  Populates the user pool with a list from the Studio plugin. Current role pulls: 'admin', 'manager', and 'artist'
|  getProjectUsers  |  {access_token}, {channel_id}  |  Populates user pool with list of current active members in a channel
|  getTeamUsers  |  {access_token}  |  Get all members in your Slack team who are not a bot, and not deativated. This list can be large
|  getMessage  |  {slack_user}, {seq}, {shot}, {product}, {sender}  |  Grab the message to be sent to the artist being notified
|  populateStudioUsers  |  {state}  |  This method will grab the access token, current project, channel id, and notify method in order to come up with the list of users needed to populate the Notify Artists combo box in the state manager. 
|  getStudioSlackConfig  |  No Arguments  |  Grabs the json data from the slack.json file in the Studio Path config location
|  getProjectConfig  |  No Arguments  |  Grabs the config json data from the pipeline.json file located in the project directory
|  isStudioLoaded  |  No Arguments  |  Checks to see if the Studio plugin exists, and is loaded
|  publishToSlack_fromMedia  |  {file}  |  This function is designed to publish the content from the Project Browser under the media tab. The main difference between this function vs the State Manager method is the amount of window popups.
|  publishToSlack_fromSM  |  {file}  |  Publish content directly from the State Manager. The main different between this function vs the Media Browser method is the amount of window popups.
|  retrieveExtension  |  {option}  |  Retrieves the extension option from the Media Conversion combo box. As long as it contains either: png, jpg, mp4, or mov in the name, it will convert to those options. For example if the option is called 'WF PNG' for the studios conversion of EXR's to a custom preset of PNG, then it will set the Extension as PNG. 
|  convertImageSequence  |  {sequence}  |  This function takes the sequence that was output from the Render or Playblast and converts the image sequence to an mp4 before publishing to Slack. This function is skipped if the Media Conversion option is enabled and set to mp4 or mov. If the Media Conversion option is enabled and it is converting to a different image type, it will convert to an mp4.
|  uploadToSlack  |  {access_token}, {channel_id}, {file}, {method}  |  Depending on the method used to upload (State Manager or Media Browser), it will upload the content to the channel associated with the project. 
|  notifySlackUser  |  {access_token}, {slack_user}, {channel_id},  {product},  {sender}  |  This function grabs the message that will be used to notify the slack user, and sends a notification to the user that an update is coming for the associated: seq, shot, product, version, etc.
|  teamsUserWarning  |  {user}  |  While Teams is not currently an option due to the reasons mentioned in the future planned options, this method was designed to popup a window warning the user they are trying to notify is not part of the channel. Calling a security concern to the user.
|  successfulPOST  |  {uploaded}, {method}  |  This function gets called after the content has been uploaded to Slack. It will display whether or not the upload was successful.
|  createSlackSubmenu  |  {toggled}, {state}  |  This menu gets triggered when the Slack option in the State Manager is selected. When it is checked/toggled on it will create the Slack submenu.
|  removeCleanupLayout  |  {layout}, {attribute_name}, {state}  |  Completely removes the Slack submenu. Needed because it would sometimes leave artifacts and cause visual bugs.


## Examples
