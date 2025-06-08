"""Добавлено поле booked_by_user_id в LunchSlot

Revision ID: 62c39cd0f28f
Revises: 63f2a5979515
Create Date: 2025-06-06 14:34:59.451000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62c39cd0f28f'
down_revision: Union[str, None] = '63f2a5979515'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('lunch_slots', schema=None) as batch_op:
        batch_op.add_column(sa.Column('booked_by_user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_lunch_slots_booked_by_user_id',  # Имя внешнего ключа
            'users',  # Таблица, на которую ссылается внешний ключ
            ['booked_by_user_id'],  # Поле в текущей таблице
            ['id']  # Поле в целевой таблице
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('lunch_slots', schema=None) as batch_op:
        batch_op.drop_constraint('fk_lunch_slots_booked_by_user_id', type_='foreignkey')
        batch_op.drop_column('booked_by_user_id')
