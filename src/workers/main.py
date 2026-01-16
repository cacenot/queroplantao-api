"""FastStream worker entry point."""

import asyncio

from faststream import FastStream

from src.app.dependencies import get_settings
from src.shared.infrastructure.messaging.broker import broker


# Create FastStream application
app = FastStream(broker)


@app.on_startup
async def on_startup() -> None:
    """Worker startup event."""
    settings = get_settings()
    print(f"Starting {settings.APP_NAME} worker...")


@app.on_shutdown
async def on_shutdown() -> None:
    """Worker shutdown event."""
    settings = get_settings()
    print(f"Shutting down {settings.APP_NAME} worker...")


# TODO: Register handlers as they are created
# Example:
# from src.app.workers.handlers import email_handler, notification_handler
# broker.include_router(email_handler.router)
# broker.include_router(notification_handler.router)


def run() -> None:
    """Run the worker."""
    asyncio.run(app.run())


if __name__ == "__main__":
    run()
