import requests
import json

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class UserPools:
    def __init__(self, core):
        self.core = core

    @err_catcher(name=__name__)
    def getTeamUsers(self, access_token):
        url = "https://slack.com/api/users.list"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)

        members = response.json().get("members")

        team_users = []

        for m in members:
            if m.get("display_name") is not None and m.get("is_bot") == False:
                team_users.append(
                    {"display_name": m.get("display_name"), "id": m.get("id")}
                )

        return team_users

    # Get the Users in a Slack Channel, saving only their display name and id
    @err_catcher(name=__name__)
    def getChannelUsers(self, access_token, conversation_id):
        url = "https://slack.com/api/conversations.members"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"channel": conversation_id}

        response = requests.get(url, headers=headers, params=params)

        channel_members = response.json()["members"]
        channel_users = []

        for m in channel_members:
            url = "https://slack.com/api/users.info"
            headers = {"Authorization": f"Bearer {access_token}"}
            params = {"user": m}

            response = requests.get(url, headers=headers, params=params)

            user = response.json().get("user")

            user_name = user["profile"].get("display_name")
            user_id = user.get("id")

            if user.get("is_bot") == False:
                channel_users.append({"id": user_id, "display_name": user_name})

        return channel_users

    @err_catcher(name=__name__)
    def getStudioUsers(self, state):
        studio = self.core.getPlugin("Studio")
        data = studio.getStudioUsers()
        users = []
        for user in data:
            if user.get("role") not in ["deactivated"]:
                users.append(user.get("name"))

        return users
