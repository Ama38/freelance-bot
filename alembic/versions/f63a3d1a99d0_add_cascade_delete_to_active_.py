"""add cascade delete to active subscriptions

Revision ID: f63a3d1a99d0
Revises: 68a23ed15b5d
Create Date: 2024-10-25 05:27:31.887514

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f63a3d1a99d0'
down_revision: Union[str, None] = '68a23ed15b5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create new table
    with op.batch_alter_table('active_subscriptions', schema=None) as batch_op:
        batch_op.drop_constraint('active_subscriptions_category_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'active_subscriptions_category_id_fkey',
            'categories',
            ['category_id'],
            ['id'],
            ondelete='CASCADE'
        )


def downgrade() -> None:
    with op.batch_alter_table('active_subscriptions', schema=None) as batch_op:
        batch_op.drop_constraint('active_subscriptions_category_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'active_subscriptions_category_id_fkey',
            'categories',
            ['category_id'],
            ['id']
        )