import requests
from config import BOT_TOKEN

#global for bot, use /guilds/{guildid}/commands for specific guilds
url = "https://discord.com/api/v8/applications/386490723223994371/commands"

json = {
    "name": "lenny",
    "description": "Send ( ͡° ͜ʖ ͡°)",
    "options": [
        {
            "name": "count",
            "description": "Number of lennys",
            "type": 4,
                # SUB_COMMAND	1
                # SUB_COMMAND_GROUP	2
                # STRING	3
                # INTEGER	4
                # BOOLEAN	5
                # USER	6
                # CHANNEL	7
                # ROLE	8
            "required": False
        }
    ]
}

# For authorization, you can use either your bot token 
headers = {
    "Authorization": f"Bot {BOT_TOKEN}"
}

r = requests.post(url, headers=headers, json=json)
print(r.json())

#https://discord.com/api/oauth2/authorize?client_id=386490723223994371&permissions=0&scope=bot%20applications.commands