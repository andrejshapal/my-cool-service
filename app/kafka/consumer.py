import datetime
import json
import threading

from kafka import KafkaConsumer

from app import Problem
from app.managers.message_manager import add_message, get_message, update_message
from app.managers.problem_manager import add_problem, get_problem, update_problem
from app.models.messages import Message

_consumer_thread: threading.Thread | None = None


def start_consumer(app, *, bootstrap_servers: str = "localhost:9092"):
    """
    Starts a Kafka consumer on specified topics asynchronously using a separate thread.
    The consumer listens for events from Kafka, processes data based on event type,
    and invokes appropriate data handling functions. If the consumer thread is
    already running, this function exits without starting a new thread.

    :param app: Instance of the Flask application used to provide application context
                and logging during consumer operations.
    :type app: Flask
    :param bootstrap_servers: Kafka bootstrap server(s) to connect to; default is
                              "localhost:9092".
    :type bootstrap_servers: str
    :return: None
    """
    global _consumer_thread

    if _consumer_thread and _consumer_thread.is_alive():
        return  # already running

    def _run():
        with app.app_context():
            app.logger.info("Kafka consumer starting (topic=%s, bootstrap=%s)", "[problems,messages]", bootstrap_servers)
            consumer = KafkaConsumer(
                "problems", "messages",
                bootstrap_servers=bootstrap_servers,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id=f"flask-problems-consumer-{datetime.datetime.now()}",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")) if v is not None else None,
            )
            try:
                for event in consumer:
                    app.logger.debug("Kafka message: %s", event)
                    payload = event.value
                    event_type = payload.get("type")
                    data = payload.get("data", {})
                    match event_type:
                        case "insert" if event.topic == "problems":
                            problem = Problem.from_dict(data)
                            add_problem(problem)
                        case "update" if event.topic == "problems":
                            update_problem(data)
                        case "insert" if event.topic == "messages":
                            message = Message.from_dict(data)
                            add_message(message)
                        case "update" if event.topic == "messages":
                            update_message(data)
                        case _:
                            raise ValueError(f"Unknown event type: {event_type!r}")
            except Exception:
                app.logger.exception("Kafka consumer crashed")
            finally:
                try:
                    consumer.close()
                except Exception:
                    app.logger.exception("Failed to close Kafka consumer")

    _consumer_thread = threading.Thread(target=_run, daemon=True)
    _consumer_thread.start()