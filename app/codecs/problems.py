from datetime import datetime
from enum import Enum
from app.models.problems import Problem


def problem_to_dict_ws(problem: Problem) -> dict:
    """
    Converts a Problem instance into a dictionary representation.

    This function takes an object of type Problem and formats its attributes
    into a dictionary with appropriate types and formats. It ensures datetime
    attributes are converted to ISO format strings and enumerated types
    are represented by their values.

    :param problem:
        A Problem object containing information about a specific problem
        such as its ID, user ID, title, description, location (latitude
        and longitude), status, and timestamps.
    :type problem: Problem
    :return:
        A dictionary containing a serialized representation of the Problem
        object. The dictionary includes the `id`, `user_id`, `title`,
        `description`, `long`, `lat`, `status`, `created_at`, and `updated_at`
        fields. `created_at` and `updated_at` are provided in ISO format strings,
        and the `status` is given as the enumerated value if applicable.
    :rtype: dict
    """
    created_at = problem.created_at
    updated_at = problem.updated_at
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()
    if isinstance(updated_at, datetime):
        updated_at = updated_at.isoformat()
    status = getattr(problem, "status", None)
    if isinstance(status, Enum):
        status = status.value

    return {
        "id": problem.id,
        "user_id": problem.user_id,
        "title": problem.title,
        "description": problem.description,
        "long": problem.long,
        "lat": problem.lat,
        "status": status,
        "created_at": created_at,
        "updated_at": updated_at,
    }