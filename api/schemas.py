from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class MessageBase(BaseModel):
    text: Optional[str] = None
    views: Optional[int] = 0
    forwards: Optional[int] = 0
    has_media: bool = False


class Message(MessageBase):
    message_id: int
    channel_id: int
    date_key: datetime

    class Config:
        orm_mode = True


class Detection(BaseModel):
    detection_id: int
    image_path: str
    product_label: str
    score: float


class TopProduct(BaseModel):
    label: str
    count: int


class ChannelActivityPoint(BaseModel):
    date: datetime
    count: int


class MessageSearchResult(BaseModel):
    message_id: int
    channel_id: int
    date: datetime
    text: Optional[str]
