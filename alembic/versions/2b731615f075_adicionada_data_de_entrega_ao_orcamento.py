"""adicionada data de entrega ao orcamento

Revision ID: 2b731615f075
Revises: f3ae46061802
Create Date: 2025-08-01 09:30:40.763618

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b731615f075'
down_revision: Union[str, None] = 'f3ae46061802'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('orcamento', sa.Column('data_entrega', sa.DateTime(timezone=False), nullable=True))


def downgrade() -> None:
    op.drop_column('orcamento', 'data_entrega')