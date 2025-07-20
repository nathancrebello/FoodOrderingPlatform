"""empty message

Revision ID: f2dafb45d72a
Revises: fd1883cbbbcd
Create Date: 2025-01-01 12:53:02.950129

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2dafb45d72a'
down_revision: Union[str, None] = 'fd1883cbbbcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'order_processing',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('transcription', sa.Text, nullable=False),
        sa.Column('order_details', sa.Text, nullable=False)
    )

def downgrade():
    op.drop_table('order_processing')
