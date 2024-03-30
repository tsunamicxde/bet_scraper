from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bot import send_notification

app = FastAPI()


class Notification(BaseModel):
    message: str


@app.post("/send-notification/")
async def api_send_message(notification: Notification):
    try:
        await send_notification(notification.message)
        return {"message": "Notification sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
