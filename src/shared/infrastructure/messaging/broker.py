"""FastStream broker configuration for LavinMQ/RabbitMQ."""

from faststream.rabbit import RabbitBroker

from src.app.dependencies import get_settings


def create_broker() -> RabbitBroker:
    """Create and configure LavinMQ broker."""
    settings = get_settings()

    broker = RabbitBroker(
        url=settings.LAVINMQ_URL,
        graceful_timeout=10,
    )

    return broker


# Global broker instance
broker = create_broker()
