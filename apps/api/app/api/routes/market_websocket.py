import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.core.logging import logger
from app.schemas.market_websocket import (
    MarketSubscribed,
    MarketSubscription,
    MarketWebSocketError,
)
from app.services.market_stream import MarketStreamEvent, market_stream_hub

router = APIRouter()


async def send_validation_error(
    websocket: WebSocket, error: ValidationError | ValueError
) -> None:
    payload = MarketWebSocketError(
        code="invalid_subscription",
        message="Expected a subscribe message with a valid symbol and timeframe.",
    )
    await websocket.send_json(payload.model_dump(mode="json"))
    logger.debug("Rejected market WebSocket message: %s", error)


async def receive_subscription(websocket: WebSocket) -> MarketSubscription | None:
    try:
        message = await websocket.receive_json()
        return MarketSubscription.model_validate(message)
    except (ValidationError, ValueError) as error:
        await send_validation_error(websocket, error)
        return None


@router.websocket("/ws/market")
async def market_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    subscription: MarketSubscription | None = None
    stream_queue: asyncio.Queue[MarketStreamEvent] | None = None
    receive_task: asyncio.Task[MarketSubscription | None] | None = None
    stream_task: asyncio.Task[MarketStreamEvent] | None = None

    try:
        receive_task = asyncio.create_task(receive_subscription(websocket))
        while True:
            pending = {receive_task}
            if stream_task is not None:
                pending.add(stream_task)
            completed, _ = await asyncio.wait(
                pending, return_when=asyncio.FIRST_COMPLETED
            )

            if receive_task in completed:
                next_subscription = receive_task.result()
                receive_task = asyncio.create_task(receive_subscription(websocket))
                if next_subscription is None:
                    continue

                if subscription is not None and stream_queue is not None:
                    await market_stream_hub.unsubscribe(subscription, stream_queue)
                if stream_task is not None:
                    stream_task.cancel()
                    await asyncio.gather(stream_task, return_exceptions=True)

                subscription = next_subscription
                stream_queue = await market_stream_hub.subscribe(subscription)
                stream_task = asyncio.create_task(stream_queue.get())
                acknowledgement = MarketSubscribed(
                    symbol=subscription.symbol,
                    timeframe=subscription.timeframe,
                )
                await websocket.send_json(acknowledgement.model_dump(mode="json"))
                continue

            if stream_task is not None and stream_task in completed:
                event = stream_task.result()
                await websocket.send_json(event.model_dump(mode="json"))
                if stream_queue is not None:
                    stream_task = asyncio.create_task(stream_queue.get())
    except WebSocketDisconnect:
        logger.debug("Market WebSocket client disconnected")
    finally:
        if subscription is not None and stream_queue is not None:
            await market_stream_hub.unsubscribe(subscription, stream_queue)
        for task in (receive_task, stream_task):
            if task is not None:
                task.cancel()
        await asyncio.gather(
            *(task for task in (receive_task, stream_task) if task is not None),
            return_exceptions=True,
        )
