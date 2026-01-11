import uuid
from datetime import datetime, UTC
from enum import Enum
import time

from app.models.users import User

class Status(Enum):
    """
    Represents a set of possible statuses for a given entity.

    This enumeration is used to define the possible state values
    that an entity can be in, such as Pending, Open, Closed, or
    Rejected. It ensures a predefined set of legal status values
    and can be used for state validation or constraint purposes.
    The values are represented as strings.

    """
    Pending = "pending"
    Open = "open"
    Closed = "closed"
    Rejected = "rejected"

class Problem:
    """
    Represents a reported problem entity in the system.

    This class models a problem reported by a user, containing
    details such as its identifier, associated user, geographical
    location, status, and timestamps. It includes methods for data
    ingestion, updates, and interaction with associated user data.

    :ivar id: Unique identifier of the problem.
    :type id: str
    :ivar user_id: Identifier of the user who reported the problem.
    :type user_id: int
    :ivar title: Short title describing the problem.
    :type title: str
    :ivar description: Full description of the problem details.
    :type description: str
    :ivar long: Longitude coordinate of the problem's location.
    :type long: float
    :ivar lat: Latitude coordinate of the problem's location.
    :type lat: float
    :ivar status: Current status of the problem (e.g., Pending, Resolved).
    :type status: Status
    :ivar created_at: Timestamp indicating when the problem was created.
    :type created_at: datetime
    :ivar updated_at: Timestamp indicating when the problem was last updated.
    :type updated_at: datetime
    """
    id: str
    user_id: int
    title: str
    description: str
    long: float
    lat: float
    status: Status
    created_at: datetime
    updated_at: datetime

    def __init__(self, user_id, title, description, long, lat, created_at, updated_at, *, problem_id: str | None = None, status: Status = Status.Pending):
        self.id = str(problem_id) if problem_id is not None else str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.description = description
        self.long = long
        self.lat = lat
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_dict(cls, data: dict) -> "Problem":
        # Expecting Kafka payload to contain at least these fields.
        # created_at/updated_at may arrive as ISO strings; keep as-is if you already handle it elsewhere.
        return cls(
            problem_id=data.get("id"),
            user_id=data.get("user_id"),
            title=data.get("title"),
            description=data.get("description"),
            long=data.get("long"),
            lat=data.get("lat"),
            status=data.get("status"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def update(self, values):
        for key, value in values.items():
            if hasattr(self, key) and value is not None:
                # Skip the ID to prevent it from being modified during a partial update
                if key == 'id':
                    continue
                setattr(self, key, value)
        self.updated_at = datetime.now(UTC)

    @property
    def user(self):
        u = User.query.filter_by(id=self.user_id).first()
        if u:
            return u
        return None