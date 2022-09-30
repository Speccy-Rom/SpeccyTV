import logging
import os
from functools import lru_cache

import ffmpeg

from core.constants import aspect_size
from db.postgres.models import Convertation
from models.convertation import ConvertVideoOut, ConvertVideoCreate, ConvertVideoIn
from services.db import create_convertation


class ConvertService:
    def __init__(self):
        pass

    @staticmethod
    async def convert(convert: ConvertVideoIn):
        res = False

        try:
            new_convert = ConvertVideoCreate(**convert.dict())
            stream = ffmpeg.input(new_convert.source_path)
            audio = stream.audio
            destination = os.path.join(
                new_convert.destination_path,
                f"{os.path.basename(new_convert.source_path).split('.')[0]}_{new_convert.resolution}.avi",
            )

            if new_convert.resolution:
                if new_convert.resolution in aspect_size:
                    logging.debug(new_convert.resolution)
                    stream = ffmpeg.filter(
                        stream,
                        "scale",
                        size=aspect_size.get(new_convert.resolution),
                        force_original_aspect_ratio="increase",
                    )

            if new_convert.fps:
                stream = ffmpeg.filter(stream, "fps", fps=new_convert.fps, round="up")

            if new_convert.codec_name:
                stream = ffmpeg.output(
                    stream, destination, format=new_convert.codec_name
                ).overwrite_output()
            else:
                stream = ffmpeg.output(audio, stream, destination).overwrite_output()
            proc = ffmpeg.run(stream)
            if proc:
                res = True

            convert_to_create: Convertation = Convertation(**new_convert.dict())
            await create_convertation(
                convert_to_create=convert_to_create
            )
            return ConvertVideoOut(result=res)
        except ffmpeg.Error as ffmpeg_err:
            logging.exception(ffmpeg_err)
            return ConvertVideoOut(result=res)


@lru_cache()
def get_convert_service() -> ConvertService:
    return ConvertService()
