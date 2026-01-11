import uuid
from datetime import datetime, UTC
import time

from app.models.users import User


class Message:
    """
    Represents a message within a chat system.

    This class encapsulates the information and functionality related to a single
    message within a chat application. Each message contains metadata such as its
    author, creation timestamp, its rating, and its visibility state (hidden or not).
    It provides methods for initialization from dictionaries (such as Kafka payloads)
    and partial updates of its attributes. Additionally, it includes access to the
    user (author) entity corresponding to the message.

    :ivar chat_id: Unique identifier of the chat to which this message belongs.
    :type chat_id: str
    :ivar message_id: Unique identifier of the message.
    :type message_id: str
    :ivar author: ID of the user who authored the message.
    :type author: int
    :ivar rating: Numerical rating assigned to the message.
    :type rating: int
    :ivar message: The content of the message.
    :type message: str
    :ivar created_at: Timestamp representing when the message was created.
    :type created_at: datetime
    :ivar hidden: Indicates whether this message is hidden (True) or visible (False).
    :type hidden: bool
    """
    chat_id: str
    message_id: str
    author: int
    rating: int
    message: str
    created_at: datetime
    hidden: bool

    def __init__(
        self,
        chat_id: str,
        author: int,
        message: str,
        *,
        message_id: str | None = None,
        rating: int = 0,
        hidden: bool = False,
        created_at: datetime = datetime.now(UTC)
    ):
        self.chat_id = chat_id
        self.message_id = str(message_id) if message_id is not None else str(uuid.uuid4())[:8]
        self.author = author
        self.rating = rating
        self.message = message
        self.created_at = created_at
        self.hidden = hidden

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        # Expecting Kafka payload to contain at least these fields.
        return cls(
            chat_id=data.get("chat_id"),
            message_id=data.get("message_id"),
            author=data.get("author"),
            rating=data.get("rating"),
            message=data.get("message"),
            created_at=data.get("created_at"),
            hidden=data.get("hidden")
        )

    def update(self, values: dict):
        for key, value in values.items():
            if hasattr(self, key) and value is not None:
                # Prevent changing primary identifier on partial update
                if key == "chat_id":
                    continue
                setattr(self, key, value)

    @property
    def user(self):
        u = User.query.filter_by(id=self.author).first()
        return u if u else None