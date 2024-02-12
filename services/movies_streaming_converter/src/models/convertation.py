import datetime
import uuid
from typing import Optional

from models.base import CustomBaseModel


class ConvertVideoIn(CustomBaseModel):
    """
    A model class representing the input parameters for a video conversion operation.

    Attributes:
        source_path (str): The path to the source video file.
        destination_path (str): The path to the destination directory where the converted video will be saved.
        resolution (str): The resolution for the converted video.
        codec_name (Optional[str]): The codec to be used for the converted video. If not provided, the original codec will be used.
        display_aspect_ratio (Optional[str]): The display aspect ratio for the converted video. If not provided, the original aspect ratio will be used.
        fps (Optional[int]): The frame rate for the converted video. If not provided, the original frame rate will be used.
    """
    source_path: str
    destination_path: str
    resolution: str
    codec_name: Optional[str] = None
    display_aspect_ratio: Optional[str] = None
    fps: Optional[int] = None


class ConvertVideoCreate(ConvertVideoIn):
    """
    A model class representing the parameters for a video conversion operation, including metadata.

    This class inherits from ConvertVideoIn and adds additional attributes for the ID and creation time of the conversion operation.

    Attributes:
        id (uuid.UUID): The unique identifier for the conversion operation. This is automatically generated upon instantiation.
        created_at (datetime.datetime): The time when the conversion operation was created. This is automatically set to the current time upon instantiation.
    """
    id: uuid.UUID = uuid.uuid4()
    created_at: datetime.datetime = datetime.datetime.now()


class ConvertVideoOut(CustomBaseModel):
    """
    A model class representing the result of a video conversion operation.

    Attributes:
        result (bool): A boolean indicating whether the conversion operation was successful.
    """
    result: bool
