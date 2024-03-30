import requests

from bet_api.api import Notification
from config import api_url


def send_message_to_api(message):
    notification_data = Notification(message=message)
    try:
        response = requests.post(api_url + "/send-notification/", json=notification_data.dict())
        response.raise_for_status()
        print("Message sent successfully to bot.")
    except Exception as e:
        print("Failed to send message to bot:", e)
