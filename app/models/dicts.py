from app.extensions import db

class Category(db.Model):
    __tablename__ = "categories"
    slug = db.Column(db.String(20), primary_key=True, unique=True)
    name = db.Column(db.String(100), nullable=False)

class Status(db.Model):
    __tablename__ = "statuses"
    slug = db.Column(db.String(20), primary_key=True, unique=True)
    name = db.Column(db.String(100), nullable=False)