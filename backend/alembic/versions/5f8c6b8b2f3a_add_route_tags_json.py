"""Add tags_json column to routes

Revision ID: 5f8c6b8b2f3a
Revises: 78e3383a93f8
Create Date: 2025-11-18 11:25:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5f8c6b8b2f3a"
down_revision: Union[str, None] = "78e3383a93f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("routes", sa.Column("tags_json", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("routes", "tags_json")

