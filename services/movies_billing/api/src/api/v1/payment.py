from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, Response
from fastapi.responses import RedirectResponse, PlainTextResponse
from pydantic.main import BaseModel

from core.auth import get_auth
from services.exceptions import AlreadyHasSubscriptions, NoActiveSubscription
from services.subscription import SubscriptionService, get_subscription_service

router = APIRouter()


@router.post(
    "/subscription",
    status_code=HTTPStatus.OK,
    response_class=RedirectResponse,
    description='Оформить подписку',
)
async def create(
        user_id: str = Depends(get_auth()),
        payment_service: SubscriptionService = Depends(get_subscription_service)
) -> RedirectResponse:
    try:
        url = await payment_service.prepare_setup_payment(user_id)
    except AlreadyHasSubscriptions:
        return Response('Subscription already exists', status_code=HTTPStatus.CONFLICT)
    return RedirectResponse(url, status_code=303)


@router.delete(
    "/subscription",
    status_code=HTTPStatus.OK,
    response_class=PlainTextResponse,
    description='Отменить подписку',
)
async def cancel(
        user_id: str = Depends(get_auth()),
        payment_service: SubscriptionService = Depends(get_subscription_service)
) -> PlainTextResponse:
    try:
        await payment_service.cancel_subscription(user_id)
    except NoActiveSubscription:
        return Response('Subscription not exists', status_code=HTTPStatus.CONFLICT)

    return PlainTextResponse('Cancelled')


@router.get(
    "/subscription/success",
    status_code=HTTPStatus.OK,
    response_class=PlainTextResponse,
    description='Успех',
)
async def subscription_success(
        session_id: str,
        payment_service: SubscriptionService = Depends(get_subscription_service)
) -> Response:
    # TODO tariff ID
    await payment_service.create_subscription(session_id, 1)
    return PlainTextResponse('Подписка успешно оформлена')


@router.get(
    "/subscription/cancel",
    status_code=HTTPStatus.OK,
    response_class=HTMLResponse,
    description='Успех',
)
async def subscription_cancel() -> PlainTextResponse:
    return PlainTextResponse('Something went wrong')


class SubscriptionStatusScheme(BaseModel):
    status: bool


@router.get(
    "/subscription",
    status_code=HTTPStatus.OK,
    response_model=SubscriptionStatusScheme,
    description='Успех',
)
async def subscription_status(
        user_id: str = Depends(get_auth()),
        subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> SubscriptionStatusScheme:
    status = await subscription_service.get_subscription_status(user_id)
    return SubscriptionStatusScheme(status=status)


@router.get(
    "/users/{user_id}/subscription",
    status_code=HTTPStatus.OK,
    response_model=SubscriptionStatusScheme,
    description='Запрос статуса подписки для пользователя',
)
async def subscription_status(
        user_id: str,
        subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> SubscriptionStatusScheme:
    status = await subscription_service.get_subscription_status(user_id)
    return SubscriptionStatusScheme(status=status)
