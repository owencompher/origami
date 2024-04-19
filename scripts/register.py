# creates or updates an application command

import requests
from config import DISCORD_CLIENT_ID, DISCORD_BOT_TOKEN


url = f"https://discord.com/api/v10/applications/{DISCORD_CLIENT_ID}/commands" # depending on global vs guild scope

json = {
    "name": "ping",
    "type": 1,
    "description": "replies pong",
}

# For authorization, you can use either your bot token
headers = {
    "Authorization": f"Bot {DISCORD_BOT_TOKEN}"
}

r = requests.post(url, headers=headers, json=json)
