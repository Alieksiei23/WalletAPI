import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker

from src.core.config import settings


rabbitmq_broker = RabbitmqBroker(url=settings.url_rm)
dramatiq.set_broker(rabbitmq_broker)
