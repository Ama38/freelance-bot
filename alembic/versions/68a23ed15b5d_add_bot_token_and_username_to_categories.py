"""add bot token and username to categories

Revision ID: 68a23ed15b5d
Revises: b6a22fa13167
Create Date: 2024-10-25 05:09:52.317058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68a23ed15b5d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new nullable columns to categories table
    op.add_column('categories', sa.Column('bot_token', sa.String(), nullable=True))
    op.add_column('categories', sa.Column('bot_username', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove the columns if needed
    op.drop_column('categories', 'bot_username')
    op.drop_column('categories', 'bot_token')
