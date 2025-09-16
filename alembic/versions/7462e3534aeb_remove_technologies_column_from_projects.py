"""remove_technologies_column_from_projects

Revision ID: 7462e3534aeb
Revises: f75e76119a26
Create Date: 2025-09-09 23:40:47.236319

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7462e3534aeb'
down_revision = 'f75e76119a26'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove the technologies column from projects table
    op.drop_column('projects', 'technologies')


def downgrade() -> None:
    # Add back the technologies column 
    op.add_column('projects', sa.Column('technologies', sa.Text(), nullable=True))