from datetime import datetime

from app.models.messages import Message


def message_to_dict_ws(message: Message) -> dict:
    """
    Converts a message object into a dictionary representation, making the data
    suitable for web socket communication or other serialization needs.

    The `created_at` attribute is converted to an ISO 8601 formatted string if it
    is of type `datetime`.

    :param message: The message object containing all related attributes to convert.
    :type message: Message

    :return: A dictionary containing key-value pairs derived from the message
        object. The dictionary includes attributes such as `chat_id`, `message_id`,
        `author`, `rating`, `message`, `created_at`, and `hidden`.
    :rtype: dict
    """
    created_at = message.created_at
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()

    return {
        "chat_id": message.chat_id,
        "message_id": message.message_id,
        "author": message.author,
        "rating": message.rating,
        "message": message.message,
        "created_at": created_at,
        "hidden": message.hidden,
    }