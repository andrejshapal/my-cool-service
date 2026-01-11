from threading import Lock
from typing import List, Dict

from flask import current_app

from app.codecs.messages import message_to_dict_ws
from app.extensions import socketio
from app.models.messages import Message

chats_dict: Dict[str, List[Message]] = {}
chats_lock = Lock()

# Helper functions for safe access
def get_chat(chat_id: str) -> list[Message]:
    """
    Retrieve the list of messages associated with a specific chat ID.

    This function accesses and retrieves messages stored in a thread-safe manner
    by acquiring a lock to ensure safe concurrent access to shared resources.

    :param chat_id: The unique identifier of the chat whose messages need to
        be retrieved.
    :type chat_id: str
    :return: A list of Message objects associated with the given chat ID. If
        no chat exists with the provided chat ID, an empty list is returned.
    :rtype: list[Message]
    """
    with chats_lock:
        return chats_dict.get(str(chat_id), [])

def add_message(message: Message) -> list[Message]:
    """
    Adds a new message to the chat history of the corresponding chat ID. This function utilizes
    a lock to ensure thread-safety when accessing the shared dictionary that stores chat data.
    If the chat ID does not exist, a new entry will be created for it. Once the message is
    added to the chat history, a notification is triggered with the updated chat snapshot.

    :param message: A Message object representing the message to be added to the chat history.
    :type message: Message
    :return: A list of Message objects representing the updated chat history for the specified chat ID.
    :rtype: list[Message]
    """
    chat_id = str(message.chat_id)
    with chats_lock:
        if chat_id not in chats_dict:
            chats_dict[chat_id] = []
        chats_dict[chat_id].append(message)
        chat_snapshot = list(chats_dict[chat_id])
    _notify_new_message(chat_id, chat_snapshot)
    return chat_snapshot

def update_message(data: Dict) -> list[Message]:
    """
    Updates a message in a chat and retrieves the updated chat snapshot.

    This function searches for a specific message within a chat by its chat ID
    and message ID. If the message is found, it updates its properties using
    the provided data. It then retrieves a snapshot of the updated chat as a list
    of messages. If the message is not found, an exception is raised.

    :param data: A dictionary containing the updated message data. Must include
        `chat_id` and `message_id` as part of the dictionary keys.
    :raises Exception: If a message with the specified chat ID and message ID
        is not found.
    :return: The updated list of messages within the chat.
    :rtype: list[Message]
    """
    with chats_lock:
        message = get_message(data.get("chat_id"), data.get("message_id"))
        if message is None:
            raise Exception("Chat with such ID is not found")
        message.update(data)
        chat_snapshot = list(chats_dict.get(str(message.chat_id), []))
    _notify_new_message(str(message.chat_id), chat_snapshot)
    return chat_snapshot

def get_message(chat_id: str, message_id: str) -> Message | None:
    """
    Retrieves a message by its `message_id` from the chat identified by `chat_id`.
    If no chat is found with the given `chat_id` or no message matches the provided
    `message_id`, `None` is returned.

    :param chat_id: The unique identifier for the chat as a string.
    :param message_id: The unique identifier for the message to be retrieved.
    :return: The message object if found, or `None` if no matching message or chat exists.
    """
    chat_id = str(chat_id)
    chat = chats_dict.get(chat_id)
    if not chat:
        return None
    for message in chat:
        if str(getattr(message, "message_id", None)) == str(message_id):
            return message
    return None

def _notify_new_message(chat_id: str, message_payload: list[Message]) -> None:
    """
    Notifies the socket listeners about a new message event for a specific chat. The message
    payload is processed and sent to the corresponding chat room identified by the chat ID.

    :param chat_id: Unique identifier of the chat to which the message belongs.
    :type chat_id: str
    :param message_payload: List of `Message` objects containing the details of the
        messages to be notified to the listeners.
    :type message_payload: list[Message]
    :return: None
    """
    socketio.emit("new_message", [message_to_dict_ws(m) for m in message_payload], to=str(chat_id))
