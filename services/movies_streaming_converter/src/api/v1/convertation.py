from fastapi import APIRouter, Depends
from models.convertation import ConvertVideoOut, ConvertVideoIn
from services.convertation import ConvertService, get_convert_service

router = APIRouter()


@router.post("/convert", response_model=ConvertVideoOut)
async def create_convert(
    convertation: ConvertVideoIn,
    convert_service: ConvertService = Depends(get_convert_service),
) -> ConvertVideoOut:
    return await convert_service.convert(
        convertation,
    )
