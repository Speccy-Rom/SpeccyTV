import uuid
from enum import Enum

from tortoise import fields
from tortoise.models import Model


class Convertation(Model):
    class ConvertationStatus(str, Enum):
        CREATED = "CREATED"
        CREATE_ERROR = "CREATE_ERROR"
        RENDER_ERROR = "RENDER_ERROR"

    id = fields.UUIDField(pk=True, default=uuid.uuid4, unique=True, nullable=False,)
    source_path = fields.TextField(null=False)
    destination_path = fields.TextField(null=False)
    resolution = fields.TextField(null=False)
    codec_name = fields.TextField(null=True)
    display_aspect_ratio = fields.TextField(null=True)
    fps = fields.IntField(null=True)
    status = fields.CharEnumField(
        ConvertationStatus, null=False, default=ConvertationStatus.CREATED
    )
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "convertations"
