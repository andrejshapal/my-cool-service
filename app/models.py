from app.extensions import db, bcrypt

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship("User", backref="role", lazy="dynamic")

class User(db.Model):
    __tablename__ = "users"
    name = db.Column(db.String(128), primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    password_hash = db.Column(db.String(), nullable=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    @property
    def role_name(self):
        r = Role.query.filter_by(id=self.role_id).first()
        if r:
            return r.name
        return None

    @role_name.setter
    def role_name(self, role_name):
        r = Role.query.filter_by(name=role_name).first()
        if r:
            self.role_id = r.id
            return
        raise AttributeError("Role is not found")

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)