import logging
import os
from functools import lru_cache

import ffmpeg

from core.constants import aspect_size
from db.postgres.models import Convertation
from models.convertation import ConvertVideoOut, ConvertVideoCreate, ConvertVideoIn
from services.db import create_convertation


class ConvertService:
    """
    A service class for handling video conversion operations.
    """

    def __init__(self):
        """
        Initialize the ConvertService class.
        """
        pass

    @staticmethod
    async def convert(convert: ConvertVideoIn):
        """
        Convert a video based on the provided parameters.

        Args:
            convert (ConvertVideoIn): An instance of ConvertVideoIn containing the video conversion parameters.

        Returns:
            ConvertVideoOut: An instance of ConvertVideoOut containing the result of the conversion operation.
        """
        res = False

        try:
            # Create a new ConvertVideoCreate instance from the provided parameters
            new_convert = ConvertVideoCreate(**convert.dict())
            # Get the input stream from the source video
            stream = ffmpeg.input(new_convert.source_path)
            # Get the audio stream from the source video
            audio = stream.audio
            # Define the destination path for the converted video
            destination = os.path.join(
                new_convert.destination_path,
                f"{os.path.basename(new_convert.source_path).split('.')[0]}_{new_convert.resolution}.avi",
            )

            # If a resolution is provided and it's in the aspect_size dictionary, apply the scale filter
            if new_convert.resolution and new_convert.resolution in aspect_size:
                logging.debug(new_convert.resolution)
                stream = ffmpeg.filter(
                    stream,
                    "scale",
                    size=aspect_size.get(new_convert.resolution),
                    force_original_aspect_ratio="increase",
                )

            # If a frame rate is provided, apply the fps filter
            if new_convert.fps:
                stream = ffmpeg.filter(stream, "fps", fps=new_convert.fps, round="up")

            # If a codec is provided, output the stream with the specified codec
            if new_convert.codec_name:
                stream = ffmpeg.output(
                    stream, destination, format=new_convert.codec_name
                ).overwrite_output()
            else:
                # If no codec is provided, output the stream with the original audio and video streams
                stream = ffmpeg.output(audio, stream, destination).overwrite_output()
            # Run the ffmpeg command
            proc = ffmpeg.run(stream)
            if proc:
                res = True

            # Create a new Convertation instance from the provided parameters
            convert_to_create: Convertation = Convertation(**new_convert.dict())
            # Save the conversion operation to the database
            await create_convertation(
                convert_to_create=convert_to_create
            )
            # Return the result of the conversion operation
            return ConvertVideoOut(result=res)
        except ffmpeg.Error as ffmpeg_err:
            # Log any ffmpeg errors
            logging.exception(ffmpeg_err)
            return ConvertVideoOut(result=res)


@lru_cache()
def get_convert_service() -> ConvertService:
    """
    Get an instance of the ConvertService class.

    This function uses the lru_cache decorator to cache the result, so subsequent calls will return the same instance.

    Returns:
        ConvertService: An instance of the ConvertService class.
    """
    return ConvertService()
