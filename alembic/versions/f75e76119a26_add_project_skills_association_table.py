"""add_project_skills_association_table

Revision ID: f75e76119a26
Revises: 6e6b0ef8870d
Create Date: 2025-09-09 23:10:53.211956

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f75e76119a26'
down_revision = '6e6b0ef8870d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the project_skills association table
    op.create_table(
        'project_skills',
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ),
        sa.PrimaryKeyConstraint('project_id', 'skill_id')
    )


def downgrade() -> None:
    # Drop the project_skills association table
    op.drop_table('project_skills')