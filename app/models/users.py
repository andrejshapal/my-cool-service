from datetime import datetime, UTC

from app.extensions import db, bcrypt

class User(db.Model):
    """
    Represents a user entity within the database.

    This class defines the structure for user information, including fields such as
    name, email, configuration, and password. It supports password hashing, verification,
    and JWT claim generation for secure interaction with user data.

    :ivar id: Unique identifier for the user.
    :type id: int
    :ivar name: Full name of the user.
    :type name: str
    :ivar email: User's unique email address.
    :type email: str
    :ivar config: Optional JSON-encoded configuration settings for the user.
    :type config: dict, optional
    :ivar created_at: Timestamp of when the user record was created.
    :type created_at: datetime
    :ivar updated_at: Timestamp of when the user record was last updated.
    :type updated_at: datetime
    :ivar hidden: Indicates whether the user's profile is hidden.
    :type hidden: bool
    :ivar password_hash: Hashed representation of the user's password.
    :type password_hash: str
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    config = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    hidden = db.Column(db.Boolean, nullable=False, default=False)
    password_hash = db.Column(db.String(), nullable=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
    #
    # @property
    # def role_name(self):
    #     r = Role.query.filter_by(id=self.role_id).first()
    #     if r:
    #         return r.name
    #     return None
    #
    # @role_name.setter
    # def role_name(self, role_name):
    #     r = Role.query.filter_by(name=role_name).first()
    #     if r:
    #         self.role_id = r.id
    #         return
    #     raise AttributeError("Role is not found")

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def jwt_claims(self):
        return {
            "name": self.name,
            "email": self.email,
        }

class Admin(db.Model):
    """
    Represents an admin entity in the database.

    This class is used to define the database structure and associated behavior
    for admins in the system. Each instance of this class corresponds to a single
    record in the admins table. It includes attributes to store location data,
    associations with users, and metadata about when the record was created
    and last updated.

    :ivar id: The unique identifier for the admin.
    :type id: int
    :ivar user_id: The foreign key referencing the user associated with the admin.
    :type user_id: int
    :ivar long: The longitude coordinate for the admin's location.
    :type long: decimal.Decimal
    :ivar lat: The latitude coordinate for the admin's location.
    :type lat: decimal.Decimal
    :ivar radius: The radius defining the admin's operational or observation area.
    :type radius: int
    :ivar created_at: The timestamp indicating when the record was created.
    :type created_at: datetime.datetime
    :ivar updated_at: The timestamp indicating when the record was last updated.
    :type updated_at: datetime.datetime
    :ivar created_by: The foreign key referencing the user who created the admin record.
    :type created_by: int
    """
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    long = db.Column(db.Numeric(9,6), nullable=False)
    lat = db.Column(db.Numeric(8,6), nullable=False)
    radius = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    @property
    def user(self):
        u = User.query.filter_by(id=self.user_id).first()
        if u:
            return u
        return None

    @property
    def created_by_user(self):
        u = User.query.filter_by(id=self.created_by).first()
        if u:
            return u
        return None

class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    long = db.Column(db.Numeric(9,6), nullable=True)
    lat = db.Column(db.Numeric(8,6), nullable=True)
    radius = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    problem_id = db.Column(db.Integer, nullable=True)

    @property
    def user(self):
        u = User.query.filter_by(id=self.user_id).first()
        if u:
            return u
        return None
