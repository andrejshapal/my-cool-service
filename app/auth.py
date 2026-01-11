from app.models.users import User

def auth(username, password) -> User | None:
    """
    Authenticates a user based on credentials provided.

    This function takes in a username and a password, checks if a user with the
    given username exists, and validates the password against the stored
    credentials. If a match is found, it returns the corresponding user
    object. Otherwise, an exception is raised if the credentials are invalid.

    :param username: The username of the user to authenticate.
    :type username: str
    :param password: The password associated with the given username.
    :type password: str
    :return: The user object if authentication is successful, or None if the
        user does not exist.
    :rtype: User | None
    :raises Exception: If the username and password combination is invalid or
        an error occurs during database querying.
    """
    try:
        user = User.query.filter_by(name=username).first()
    except Exception as error:
        raise error
    if user is not None and user.verify_password(password):
        return user
    raise Exception("Invalid username or password")