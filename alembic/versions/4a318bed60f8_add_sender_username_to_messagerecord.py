"""Add sender_username to MessageRecord

Revision ID: 4a318bed60f8
Revises: 
Create Date: 2024-09-30 19:50:04.823727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a318bed60f8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('messages', sa.Column('sender_username', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('messages', 'sender_username')
