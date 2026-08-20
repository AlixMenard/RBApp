import requests
from dotenv import load_dotenv
import os
load_dotenv()

BOT_TOKEN = os.getenv("DS_BOT_TOKEN")

def DM(giver_id: str, giver: str, receiver_id: str, receiver: str):

    msg_receiver = f"Good news! It seems that {giver} has some cards that you are looking for!"
    msg_giver = f"Good news! It seems that {receiver} is interested in some cards that you have!"

    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    dm_url = "https://discord.com/api/v10/users/@me/channels"

    dm_data_giver = {"recipient_id": giver_id}
    response = requests.post(dm_url, headers=headers, json=dm_data_giver)
    if response.status_code == 200:
        channel_id = response.json()["id"]
        message_url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        message_data = {"content": msg_giver}
        response = requests.post(message_url, headers=headers, json=message_data)
        print(response.json())

    dm_data_receiver = {"recipient_id": receiver_id}
    response = requests.post(dm_url, headers=headers, json=dm_data_receiver)
    if response.status_code == 200:
        channel_id = response.json()["id"]
        message_url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        message_data = {"content": msg_receiver}
        response = requests.post(message_url, headers=headers, json=message_data)
        print(response.json())