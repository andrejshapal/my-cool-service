"""data

Revision ID: 22683f0d5d42
Revises: 5491504701e3
Create Date: 2025-11-22 21:00:32.787954

"""
from alembic import op
import sqlalchemy as sa
from flask import current_app

from app.models.users import User, Admin

# revision identifiers, used by Alembic.
revision = '22683f0d5d42'
down_revision = '5491504701e3'
branch_labels = None
depends_on = None


def upgrade():
    admin = User(name="admin", email="admin@localhost", password=current_app.config["ADMIN_PASS"])
    op.bulk_insert(
        User.__table__ , [
            {
                'name': admin.name,
                'email': admin.email,
                'password_hash': admin.password_hash,
            },
        ])
    op.bulk_insert(
        Admin.__table__ , [
            {
                'user_id': 1,
                'long': 24.11630043466352,
                'lat': 56.9508265038635,
                'radius': 6371000,
                'created_by': 1,
            },
        ])

def downgrade():
    op.execute("DELETE FROM admins")
    op.execute("DELETE FROM users")
