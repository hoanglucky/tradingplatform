import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.core.config import settings
from app.core.logging import logger
from app.schemas.market_websocket import (
    MarketHeartbeat,
    MarketPong,
    MarketSubscribed,
    MarketSubscription,
    MarketWebSocketError,
)
from app.services.market_stream import (
    MarketStreamEvent,
    market_source_for_symbol,
    market_stream_hub,
)

router = APIRouter()
ClientMessage = MarketSubscription | MarketPong


async def send_validation_error(
    websocket: WebSocket,
    error: ValidationError | ValueError,
    *,
    code: str = "invalid_subscription",
    message: str = "Expected a subscribe message with a valid symbol and timeframe.",
) -> None:
    payload = MarketWebSocketError(
        code=code,
        message=message,
    )
    await websocket.send_json(payload.model_dump(mode="json"))
    logger.debug("Rejected market WebSocket message: %s", error)


async def receive_client_message(websocket: WebSocket) -> ClientMessage | None:
    try:
        message = await websocket.receive_json()
        if isinstance(message, dict) and message.get("type") == "pong":
            try:
                return MarketPong.model_validate(message)
            except ValidationError as error:
                await send_validation_error(
                    websocket,
                    error,
                    code="invalid_pong",
                    message="Expected a pong message with the latest heartbeat id.",
                )
                return None
        return MarketSubscription.model_validate(message)
    except (ValidationError, ValueError) as error:
        await send_validation_error(websocket, error)
        return None


@router.websocket("/ws/market")
async def market_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    subscription: MarketSubscription | None = None
    stream_queue: asyncio.Queue[MarketStreamEvent] | None = None
    receive_task: asyncio.Task[ClientMessage | None] | None = None
    stream_task: asyncio.Task[MarketStreamEvent] | None = None
    heartbeat_task: asyncio.Task[None] | None = None
    heartbeat_id = 0
    last_pong_at = asyncio.get_running_loop().time()

    try:
        receive_task = asyncio.create_task(receive_client_message(websocket))
        heartbeat_task = asyncio.create_task(
            asyncio.sleep(settings.market_ws_heartbeat_seconds)
        )
        while True:
            pending = {receive_task, heartbeat_task}
            if stream_task is not None:
                pending.add(stream_task)
            completed, _ = await asyncio.wait(
                pending, return_when=asyncio.FIRST_COMPLETED
            )

            if receive_task in completed:
                client_message = receive_task.result()
                receive_task = asyncio.create_task(receive_client_message(websocket))
                if client_message is None:
                    continue
                if isinstance(client_message, MarketPong):
                    if client_message.id == heartbeat_id:
                        last_pong_at = asyncio.get_running_loop().time()
                    continue
                next_subscription = client_message

                if subscription == next_subscription:
                    acknowledgement = MarketSubscribed(
                        symbol=subscription.symbol,
                        timeframe=subscription.timeframe,
                        source=market_source_for_symbol(subscription.symbol),
                    )
                    await websocket.send_json(acknowledgement.model_dump(mode="json"))
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
                    source=market_source_for_symbol(subscription.symbol),
                )
                await websocket.send_json(acknowledgement.model_dump(mode="json"))
                continue

            if heartbeat_task in completed:
                now = asyncio.get_running_loop().time()
                if now - last_pong_at >= settings.market_ws_stale_seconds:
                    logger.info("Closing stale market WebSocket client")
                    await websocket.close(code=1001, reason="Heartbeat timeout")
                    break
                heartbeat_id += 1
                heartbeat = MarketHeartbeat(
                    id=heartbeat_id,
                    timestamp=datetime.now(timezone.utc),
                )
                await websocket.send_json(heartbeat.model_dump(mode="json"))
                heartbeat_task = asyncio.create_task(
                    asyncio.sleep(settings.market_ws_heartbeat_seconds)
                )
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
        for task in (receive_task, stream_task, heartbeat_task):
            if task is not None:
                task.cancel()
        await asyncio.gather(
            *(
                task
                for task in (receive_task, stream_task, heartbeat_task)
                if task is not None
            ),
            return_exceptions=True,
        )
