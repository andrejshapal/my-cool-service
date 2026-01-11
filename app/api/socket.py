from datetime import datetime
from typing import List

from flask_socketio import join_room, emit

from app.codecs.messages import message_to_dict_ws
from app.codecs.problems import problem_to_dict_ws
from app.extensions import socketio
from app.managers.message_manager import get_chat
from app.managers.problem_manager import get_problems


@socketio.on("join_chat")
def on_join_chat(data):
    chat_id = data.get("chat_id") if isinstance(data, dict) else None
    if not chat_id:
        emit("error", {"error": "chat_id is required"})
        return

    join_room(chat_id)
    chat = get_chat(chat_id)  # list[Message]
    emit("joined", [message_to_dict_ws(m) for m in chat])

@socketio.on("join_map")
def on_join_map():
    """
    One shared room for live problem updates.
    """
    room = "map"
    join_room(room)
    problems = get_problems()
    emit("map_joined", [problem_to_dict_ws(p) for p in problems])