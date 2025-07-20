"""Initial

Revision ID: 4019d0f755d9
Revises: 
Create Date: 2024-12-08 21:43:31.813294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4019d0f755d9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('username', sa.String(), unique=True,
                  index=True, nullable=False),
        sa.Column('email', sa.String(), unique=True,
                  index=True, nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), default=False, nullable=False),
        sa.Column('token', sa.String(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), default=False, nullable=False)
    )


def downgrade() -> None:
    op.drop_table('users')
