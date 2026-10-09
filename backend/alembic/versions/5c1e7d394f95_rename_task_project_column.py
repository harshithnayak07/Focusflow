"""rename task project column

Revision ID: 5c1e7d394f95
Revises: 3d5a0893c8ba
Create Date: 2026-10-06 07:46:12.812671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c1e7d394f95'
down_revision: Union[str, Sequence[str], None] = '3d5a0893c8ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "tasks",
        "projects_id",
        new_column_name="project_id"
    )


def downgrade() -> None:
    op.alter_column(
        "tasks",
        "project_id",
        new_column_name="projects_id"
    )
