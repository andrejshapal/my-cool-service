from logging import exception
from threading import Lock
from typing import List

from app.extensions import socketio

from app.codecs.problems import problem_to_dict_ws
from app.models.problems import Problem

problems_list: List[Problem] = []
problems_lock = Lock()

# Helper functions for safe access
def get_problems() -> List[Problem]:
    """
    Retrieves the list of problems.

    This function provides access to a predefined list of problems.

    :return: The list of problems.
    :rtype: List[Problem]
    """
    return problems_list


def add_problem(problem: Problem):
    """
    Adds a new problem to the list of problems under a thread-safe lock, updates the
    snapshot of the problems list, and emits an event to notify about the updated
    problems list.

    :param problem: The problem object to add.
    :type problem: Problem
    :return: An updated snapshot of the problems list after adding the new problem.
    :rtype: list
    """
    with problems_lock:
        problems_list.append(problem)
        problems_snapshot = list(problems_list)
    _emit_problem_event(problems_snapshot)
    return problems_snapshot

def update_problem(data):
    """
    Updates a problem using the provided data. The function retrieves the problem
    by its ID, updates it safely within a locked environment, and then emits
    a problem event with the updated snapshot of problems.

    :param data: A dictionary containing the problem ID and other fields to update.
    :type data: dict
    :return: The updated snapshot of the problems.
    :rtype: list
    :raises Exception: If the problem with the specified ID is not found.
    """
    with problems_lock:
        problem = get_problem(data.get("id"))
        if problem is None:
            raise Exception("Problem with such ID is not found")
        problem.update(data)
        problems_snapshot = list(problems_list)
    _emit_problem_event(problems_snapshot)
    return problems_snapshot

def get_problem(problem_id) -> Problem | None:
    """
    Fetches a problem object based on a given problem ID. Iterates through a
    predefined list of problems to search for a matching ID. If the problem is
    found, it is returned; otherwise, the function returns None.

    :param problem_id: The unique identifier for the problem to retrieve.
    :type problem_id: int | str
    :return: The problem object if a match is found; otherwise, None.
    :rtype: Problem | None
    """
    for problem in problems_list:
        if problem.id == str(problem_id):
            return problem
    return None

def _emit_problem_event(problems: List[Problem]) -> None:
    """
    Emits a "new_problem" event to the "map" channel with the provided list
    of problem data converted into dictionary format.

    :param problems: List of Problem instances to be emitted
    :type problems: List[Problem]
    :return: None
    """
    socketio.emit("new_problem", [problem_to_dict_ws(p) for p in problems], to="map")