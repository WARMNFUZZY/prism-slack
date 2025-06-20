import requests


# Get the users information
def get_user_info(access_token, user_id):
    url = "https://slack.com/api/users.info"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {"user": user_id}

    try:
        response = requests.get(url, headers=headers, params=payload)
        user_info = response.json()["user"]

    except Exception as e:
        print(f"Error getting user info: {e}")
        return

    return user_info


# Get Slack Channel ID from conversation list
def get_channel_id(access_token, project_name):
    url = "https://slack.com/api/conversations.list"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"limit": 1000}
    next_cursor = None

    try:
        while True:
            if next_cursor:
                params["cursor"] = next_cursor
            response = requests.get(url, headers=headers, params=params)
            conversations = response.json()

            for conversation in conversations.get("channels", []):
                if conversation["name"] == project_name:
                    return conversation["id"]

            next_cursor = conversations.get("response_metadata", {}).get("next_cursor")
            if not next_cursor:
                break

    except Exception as e:
        print(f"Error getting channel ID: {e}")
        return None


# Get the Users in a Slack Channel, saving only their display name and id
def get_channel_users(access_token, channel_id):
    url = "https://slack.com/api/conversations.members"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"channel": channel_id}

    response = requests.get(url, headers=headers, params=params)

    channel_members = response.json()["members"]
    channel_users = []

    for m in channel_members:
        url = "https://slack.com/api/users.info"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"user": m}

        response = requests.get(url, headers=headers, params=params)

        user = response.json().get("user")

        try:
            user_name = user["profile"].get("display_name")
        except:
            user_name = user["profile"].get("real_name")

        user_id = user.get("id")

        if user.get("is_bot") == False:
            channel_users.append({"id": user_id, "display_name": user_name})

    return channel_users


def get_studio_users(core):
    studio = core.getPlugin("Studio")
    data = studio.getStudioUsers()
    users = []
    for user in data:
        if user.get("role") not in ["deactivated"]:
            users.append(user.get("name"))

    return users
