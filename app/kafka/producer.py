import json
import uuid
from datetime import datetime, UTC
from decimal import Decimal
from enum import Enum
from typing import Any

from kafka import KafkaProducer

from app.models.messages import Message
from app.models.problems import Problem


def _json_default(o: Any):
    """
    Handle the encoding of non-serializable Python objects to JSON-supported types,
    including datetime, Enum, Decimal, and UUID objects. This function converts
    these types into formats compatible with JSON serialization. If the provided
    object is not supported, it raises a TypeError.

    :param o: Any Python object. The object to check and convert if it is of
              a type not supported by JSON serialization.
    :type o: Any

    :return: JSON-serializable equivalent of the input object, such as ISO 8601
             string for datetime, value for Enum, float for Decimal, or string for UUID.
    :rtype: Union[str, float]

    :raises TypeError: If the input object is not one of the handled types
                       (datetime, Enum, Decimal, uuid.UUID) or cannot be serialized.
    """
    if isinstance(o, datetime):
        return o.isoformat()
    if isinstance(o, Enum):
        return o.value
    if isinstance(o, Decimal):
        return float(o)
    if isinstance(o, uuid.UUID):
        return str(o)
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")


def problem_to_dict(problem: Problem) -> dict[str, Any]:
    """
    Converts a Problem instance to a dictionary representation.

    This function transforms the attributes of the `Problem` object into
    a dictionary format that can be used for serialization, data transfer,
    or further processing. All relevant information from the `Problem`
    instance is captured in the dictionary structure.

    :param problem: An instance of the `Problem` class containing various
        attributes such as `id`, `user_id`, `title`, `description`,
        `coordinates` (`long` and `lat`), `status`, and timestamps for
        creation and updates.
    :type problem: Problem
    :return: A dictionary containing the mapped attributes of the
        `Problem` instance.
    :rtype: dict[str, Any]
    """
    return {
        "id": problem.id,
        "user_id": problem.user_id,
        "title": problem.title,
        "description": problem.description,
        "long": problem.long,
        "lat": problem.lat,
        "status": problem.status,  # Enum handled by _json_default
        "created_at": problem.created_at,
        "updated_at": problem.updated_at,
    }

def message_to_dict(message: Message) -> dict[str, Any]:
    """
    Convert a Message object into a dictionary representation.

    This function takes a Message object containing details such as chat_id,
    message_id, author, rating, and other relevant fields, and returns a dictionary
    representation of this object. The dictionary provides a structured format
    for easier manipulation or storage of the message data.

    :param message: Instance of the Message class to be converted into a dictionary.
    :type message: Message
    :return: Dictionary containing the serialized representation of the Message
        object with its attributes as key-value pairs.
    :rtype: dict[str, Any]
    """
    return {
        "chat_id": message.chat_id,
        "message_id": message.message_id,
        "author": message.author,
        "rating": message.rating,
        "message": message.message,
        "created_at": message.created_at,
        "hidden": message.hidden,
    }

def update_to_dict(values: dict[str, Any]) -> dict[str, Any]:
    """
    Filters and retains only key-value pairs in the input dictionary where values are
    not None. This function is useful for removing fields with None values from a
    dictionary.

    :param values: A dictionary containing key-value pairs to filter
    :return: A dictionary with key-value pairs where values are not None
    """
    # Keep only provided fields (skip None)
    return {k: v for k, v in values.items() if v is not None}

def _make_event(event_type: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Creates an event dictionary with a unique identifier, version, type, timestamp,
    and associated data. The event ID is generated as a UUID. The method ensures
    that the event dictionary contains all required metadata and payload information.

    :param event_type: The type of the event to be created.
    :type event_type: str
    :param data: A dictionary containing the payload or metadata for the event.
    :type data: dict[str, Any]
    :return: A dictionary representing the event with metadata and payload.
    :rtype: dict[str, Any]
    """
    return {
        "event_id": str(uuid.uuid4()),
        "version": 1,
        "type": event_type,
        "created_at": datetime.now(UTC),
        "data": data,
    }


class Producer:
    """
    Handles producing events to Kafka.

    Provides the functionality to produce `insert` and `update` events for problems and
    messages to Kafka topics. Allows flushing and closing of the producer connection.

    :ivar producer: Kafka producer instance initialized with specific `bootstrap_servers`
        and serialization configurations.
    :type producer: KafkaProducer
    """
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=_json_default).encode("utf-8"),
            key_serializer=lambda k: str(k).encode("utf-8") if k is not None else None,
        )

    def insert_problem(self, problem: Problem, *, flush: bool = False):
        """
        Insert a problem event into the Kafka topic.

        This method formats the given Problem instance into a dictionary and creates an
        event of type "insert." The event is then sent to the Kafka topic named "problems"
        using the producer. Optionally, if the `flush` parameter is set to True, the producer
        flushes all pending messages. The method finally returns the Kafka `future` object
        associated with the send operation, which can be used for tracking delivery status.

        :param problem: Instance of `Problem` to be inserted.
        :type problem: Problem
        :param flush: Whether to flush the Kafka producer after sending the event. Defaults to False.
        :type flush: bool
        :return: Kafka future object tracking the delivery status of the message.
        :rtype: concurrent.futures.Future
        """
        event = _make_event("insert", problem_to_dict(problem))
        future = self.producer.send("problems", key=problem.id, value=event)
        if flush:
            self.producer.flush()
        return future

    def update_problem(self, values: dict[str, Any], *, flush: bool = False):
        """
        Updates a problem record with the provided values. This function sends the
        updated problem data to the 'problems' topic and optionally flushes the
        producer to ensure immediate delivery. The `values` must include an 'id'
        key, which uniquely identifies the problem to update.

        :param values: A dictionary containing the problem data to update. Must
            include an 'id' key.
        :type values: dict[str, Any]
        :param flush: A flag indicating whether the producer should flush to ensure
            the message is sent immediately. Defaults to False.
        :type flush: bool, optional
        :return: A future object representing the asynchronous send result.
        :rtype: kafka.Future
        :raises ValueError: If 'id' is not included in the provided `values`.
        """
        if not values.get("id"):
            raise ValueError("update_problem requires values['id'] (problem id)")

        data = update_to_dict(values)
        event = _make_event("update", data)
        future = self.producer.send("problems", key=str(values["id"]), value=event)
        if flush:
            self.producer.flush()
        return future

    def insert_message(self, message: Message, *, flush: bool = False):
        """
        Insert a message into the messaging system. This function takes a `Message` object,
        prepares an event with type "insert" from the provided message, and sends it to
        the "messages" topic. Optionally waits until all prior messages have been
        acknowledged by the producer when `flush` is set to True.

        :param message: The message object to be inserted.
        :type message: Message
        :param flush: Whether to flush the producer after sending the message.
        :type flush: bool
        :return: A future object representing the result of the send operation.
        :rtype: kafka.Future
        """
        event = _make_event("insert", message_to_dict(message))
        future = self.producer.send("messages", key=message.chat_id, value=event)
        if flush:
            self.producer.flush()
        return future

    def update_message(self, values: dict[str, Any], *, flush: bool = False):
        """
        Updates the message with provided values and sends it to the message broker.

        This function takes a dictionary of values to update a message, converts it
        to a specific event format, and sends it to the 'messages' topic of the
        message producer. If `flush` is set to True, it flushes the producer after
        sending the message.

        :param values: Dictionary containing the message data. It must include
            a 'chat_id' key.
        :type values: dict[str, Any]
        :param flush: Whether to flush the producer after sending the message.
        :type flush: bool
        :return: A future object representing the result of the send operation.
        :rtype: Any
        :raises ValueError: If 'chat_id' is not present in the values.
        """
        if not values.get("chat_id"):
            raise ValueError("update_chat requires values['chat_id']")

        data = update_to_dict(values)
        event = _make_event("update", data)
        future = self.producer.send("messages", key=str(values["chat_id"]), value=event)
        if flush:
            self.producer.flush()
        return future

    def close(self):
        self.producer.flush()
        self.producer.close()

producer = Producer()
