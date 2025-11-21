"""Add other named insureds table

Revision ID: 0e8f4d6c2f3b
Revises: 38136bc82556
Create Date: 2025-11-13 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0e8f4d6c2f3b'
down_revision = '38136bc82556'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use existing enum type (created in previous migration)
    business_structure_enum = postgresql.ENUM('INDIVIDUAL', 'PARTNERSHIP', 'CORPORATION', 'LLC', 'JOINT_VENTURE', 'NOT_FOR_PROFIT_ORG', 'SUBCHAPTER_S_CORPORATION', 'TRUST', name='businessstructureenum', create_type=False)
    
    op.create_table(
        'other_named_insureds',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('submission_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('mailing_address', sa.Text(), nullable=True),
        sa.Column('business_structure', business_structure_enum, nullable=True),
        sa.Column('number_of_members', sa.Integer(), nullable=True),
        sa.Column('number_of_managers', sa.Integer(), nullable=True),
        sa.Column('naics_code', sa.String(length=10), nullable=True),
        sa.Column('sic_code', sa.String(length=10), nullable=True),
        sa.Column('gl_code', sa.String(length=10), nullable=True),
        sa.Column('fein_or_ssn', sa.String(length=20), nullable=True),
        sa.Column('business_phone', sa.String(length=50), nullable=True),
        sa.Column('website_address', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_other_named_insureds_submission_id'), 'other_named_insureds', ['submission_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_other_named_insureds_submission_id'), table_name='other_named_insureds')
    op.drop_table('other_named_insureds')

