"""Add gap_analysis_results and gap_analysis_timestamp to submissions

Revision ID: add_gap_analysis_fields
Revises: 04af412b20fe
Create Date: 2025-11-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'add_gap_analysis_fields'
down_revision = '04af412b20fe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add gap_analysis_results JSON column
    op.add_column('submissions', sa.Column('gap_analysis_results', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Add gap_analysis_timestamp DateTime column
    op.add_column('submissions', sa.Column('gap_analysis_timestamp', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove gap_analysis_timestamp column
    op.drop_column('submissions', 'gap_analysis_timestamp')
    
    # Remove gap_analysis_results column
    op.drop_column('submissions', 'gap_analysis_results')















