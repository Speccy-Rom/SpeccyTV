from db.postgres.models import Convertation
from tortoise.transactions import in_transaction


async def create_convertation(convert_to_create: Convertation) -> Convertation:
    async with in_transaction() as tr:
        res_ = await Convertation.create(
            source_path=convert_to_create.source_path,
            destination_path=convert_to_create.destination_path,
            resolution=convert_to_create.resolution,
            codec_name=convert_to_create.codec_name,
            display_aspect_ratio=convert_to_create.display_aspect_ratio,
            fps=convert_to_create.fps,
            created_at=convert_to_create.created_at,
            status=convert_to_create.status,
            using_db=tr,
        )
        return res_
