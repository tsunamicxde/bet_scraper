from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import config
from automation.write_to_file import write_to_file
from bot import send_notification

app = FastAPI()


class Notification(BaseModel):
    message: str
    type_of_coefficient: str
    match_id: int


@app.post("/send-notification/")
async def api_send_message(notification: Notification):
    try:
        await send_notification(notification.message, notification.type_of_coefficient, notification.match_id)
        return {"message": "Notification sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

