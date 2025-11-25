"""add_general_questions_column

Revision ID: 4b4848f1379f
Revises: 0e8f4d6c2f3b
Create Date: 2025-11-21 10:17:51.274561

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '4b4848f1379f'
down_revision = '0e8f4d6c2f3b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('submissions', sa.Column('general_questions', postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('submissions', 'general_questions')
