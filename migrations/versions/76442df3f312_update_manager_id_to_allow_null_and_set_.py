"""Update manager_id to allow NULL and SET NULL on delete

Revision ID: 76442df3f312
Revises: 8af9191bac1e
Create Date: 2025-06-17 17:24:56.086162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76442df3f312'
down_revision: Union[str, None] = '8af9191bac1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Изменяем поле manager_id в таблице lunch_slots
    op.alter_column(
        'lunch_slots',
        'manager_id',
        existing_type=sa.Integer(),
        nullable=True
    )
    op.drop_constraint('fk_lunch_slots_manager_id_users', 'lunch_slots', type_='foreignkey')
    op.create_foreign_key(
        'fk_lunch_slots_manager_id_users',
        'lunch_slots',
        'users',
        ['manager_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем поле manager_id в исходное состояние
    op.alter_column(
        'lunch_slots',
        'manager_id',
        existing_type=sa.Integer(),
        nullable=False
    )
    op.drop_constraint('fk_lunch_slots_manager_id_users', 'lunch_slots', type_='foreignkey')
    op.create_foreign_key(
        'fk_lunch_slots_manager_id_users',
        'lunch_slots',
        'users',
        ['manager_id'],
        ['id']
    )
