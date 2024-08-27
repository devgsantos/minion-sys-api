"""Fusão de múltiplas heads

Revision ID: 8cf45dc55348
Revises: 9c5dbdf942ba, cedc32ca4805
Create Date: 2024-08-25 17:49:02.555148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8cf45dc55348'
down_revision: Union[str, None] = ('9c5dbdf942ba', 'cedc32ca4805')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
