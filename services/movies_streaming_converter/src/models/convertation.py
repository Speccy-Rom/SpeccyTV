import datetime
import uuid
from typing import Optional

from models.base import CustomBaseModel


class ConvertVideoIn(CustomBaseModel):
    source_path: str
    destination_path: str
    resolution: str
    codec_name: Optional[str] = None
    display_aspect_ratio: Optional[str] = None
    fps: Optional[int] = None


class ConvertVideoCreate(ConvertVideoIn):
    id: uuid.UUID = uuid.uuid4()
    created_at: datetime.datetime = datetime.datetime.now()


class ConvertVideoOut(CustomBaseModel):
    result: bool
