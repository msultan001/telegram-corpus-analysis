from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageBase(BaseModel):
    message_text: Optional[str] = None
    views: Optional[int] = 0
    forwards: Optional[int] = 0
    has_media: bool = False

class Message(MessageBase):
    message_id: int
    channel_id: int
    date_key: datetime

    class Config:
        orm_mode = True
