"""Update schema to match mikebgdev.com structure

Revision ID: update_schema_for_website
Revises: 13c674603dc9
Create Date: 2025-08-11 11:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision = 'update_schema_for_website'
down_revision = '13c674603dc9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create Contact table first
    op.create_table('contact',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('linkedin_url', sa.String(), nullable=True),
        sa.Column('github_url', sa.String(), nullable=True),
        sa.Column('twitter_url', sa.String(), nullable=True),
        sa.Column('instagram_url', sa.String(), nullable=True),
        sa.Column('contact_form_enabled', sa.Boolean(), nullable=True),
        sa.Column('contact_message', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contact_id'), 'contact', ['id'], unique=False)
    
    # Update About table - Add columns as nullable first
    op.add_column('about', sa.Column('name', sa.String(), nullable=True))
    op.add_column('about', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('about', sa.Column('email', sa.String(), nullable=True))
    op.add_column('about', sa.Column('location', sa.String(), nullable=True))
    op.add_column('about', sa.Column('nationality', sa.String(), nullable=True))
    op.add_column('about', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('about', sa.Column('personal_statement', sa.Text(), nullable=True))
    
    # Migrate existing content to bio field and set default values
    connection = op.get_bind()
    about_table = table('about',
        column('id', sa.Integer),
        column('content', sa.Text),
        column('name', sa.String),
        column('age', sa.Integer),
        column('email', sa.String),
        column('location', sa.String),
        column('nationality', sa.String),
        column('bio', sa.Text)
    )
    
    # Update existing records with default values
    connection.execute(
        about_table.update().values(
            name='Michael',
            age=30,
            email='mike@mikebgdev.com',
            location='Anna, Valencia',
            nationality='Spanish',
            bio=about_table.c.content
        )
    )
    
    # Now make required fields NOT NULL
    op.alter_column('about', 'name', nullable=False)
    op.alter_column('about', 'email', nullable=False)
    op.alter_column('about', 'location', nullable=False)
    op.alter_column('about', 'nationality', nullable=False)
    op.alter_column('about', 'bio', nullable=False)
    
    # Drop old content column
    op.drop_column('about', 'content')
    
    # Update Skills table
    op.add_column('skills', sa.Column('category', sa.String(), nullable=True))
    op.add_column('skills', sa.Column('is_in_progress', sa.Boolean(), nullable=True))
    op.add_column('skills', sa.Column('display_order', sa.Integer(), nullable=True))
    
    # Set default values for skills
    skills_table = table('skills',
        column('id', sa.Integer),
        column('type', sa.String),
        column('category', sa.String),
        column('is_in_progress', sa.Boolean),
        column('display_order', sa.Integer)
    )
    
    # Map old type to new category
    connection.execute(
        skills_table.update()
        .where(skills_table.c.type == 'technical')
        .values(category='web_development', is_in_progress=False, display_order=0)
    )
    connection.execute(
        skills_table.update()
        .where(skills_table.c.type == 'interpersonal')
        .values(category='interpersonal', is_in_progress=False, display_order=0)
    )
    
    # Make category NOT NULL and drop old columns
    op.alter_column('skills', 'category', nullable=False)
    op.drop_column('skills', 'type')
    op.drop_column('skills', 'level')
    
    # Update Projects table
    op.add_column('projects', sa.Column('title', sa.String(), nullable=True))
    op.add_column('projects', sa.Column('source_url', sa.String(), nullable=True))
    op.add_column('projects', sa.Column('display_order', sa.Integer(), nullable=True))
    op.add_column('projects', sa.Column('is_featured', sa.Boolean(), nullable=True))
    
    # Migrate data
    projects_table = table('projects',
        column('id', sa.Integer),
        column('name', sa.String),
        column('github_url', sa.String),
        column('title', sa.String),
        column('source_url', sa.String),
        column('display_order', sa.Integer),
        column('is_featured', sa.Boolean),
        column('image_url', sa.String),
        column('technologies', sa.String)
    )
    
    # Copy name to title and github_url to source_url
    connection.execute(
        projects_table.update().values(
            title=projects_table.c.name,
            source_url=projects_table.c.github_url,
            display_order=0,
            is_featured=False
        )
    )
    
    # Make required fields NOT NULL and set defaults
    op.alter_column('projects', 'title', nullable=False)
    op.alter_column('projects', 'image_url', nullable=False, server_default='')
    op.alter_column('projects', 'technologies', type_=sa.Text(), nullable=False, server_default='')
    
    # Drop old columns
    op.drop_column('projects', 'name')
    op.drop_column('projects', 'github_url')
    
    # Update Experience table
    op.add_column('experience', sa.Column('display_order', sa.Integer(), nullable=True))
    op.alter_column('experience', 'description', nullable=False, server_default='')
    
    # Update Education table
    op.add_column('education', sa.Column('display_order', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Reverse all changes
    op.drop_column('education', 'display_order')
    
    op.alter_column('experience', 'description', nullable=True)
    op.drop_column('experience', 'display_order')
    
    # Restore Projects table
    op.add_column('projects', sa.Column('name', sa.String(), nullable=False, server_default=''))
    op.add_column('projects', sa.Column('github_url', sa.String(), nullable=False, server_default=''))
    
    # Migrate data back
    connection = op.get_bind()
    projects_table = table('projects',
        column('title', sa.String),
        column('source_url', sa.String),
        column('name', sa.String),
        column('github_url', sa.String)
    )
    connection.execute(
        projects_table.update().values(
            name=projects_table.c.title,
            github_url=projects_table.c.source_url
        )
    )
    
    op.alter_column('projects', 'technologies', type_=sa.String(), nullable=True)
    op.alter_column('projects', 'image_url', nullable=True)
    op.drop_column('projects', 'is_featured')
    op.drop_column('projects', 'display_order')
    op.drop_column('projects', 'source_url')
    op.drop_column('projects', 'title')
    
    # Restore Skills table
    op.add_column('skills', sa.Column('level', sa.Integer(), nullable=True))
    op.add_column('skills', sa.Column('type', sa.String(), nullable=False, server_default='technical'))
    
    # Migrate category back to type
    skills_table = table('skills',
        column('category', sa.String),
        column('type', sa.String)
    )
    connection.execute(
        skills_table.update()
        .where(skills_table.c.category == 'interpersonal')
        .values(type='interpersonal')
    )
    connection.execute(
        skills_table.update()
        .where(skills_table.c.category != 'interpersonal')
        .values(type='technical')
    )
    
    op.drop_column('skills', 'display_order')
    op.drop_column('skills', 'is_in_progress')
    op.drop_column('skills', 'category')
    
    # Restore About table
    op.add_column('about', sa.Column('content', sa.Text(), nullable=False, server_default=''))
    
    # Migrate bio back to content
    about_table = table('about',
        column('bio', sa.Text),
        column('content', sa.Text)
    )
    connection.execute(
        about_table.update().values(content=about_table.c.bio)
    )
    
    op.drop_column('about', 'personal_statement')
    op.drop_column('about', 'bio')
    op.drop_column('about', 'nationality')
    op.drop_column('about', 'location')
    op.drop_column('about', 'email')
    op.drop_column('about', 'age')
    op.drop_column('about', 'name')
    
    # Drop Contact table
    op.drop_index(op.f('ix_contact_id'), table_name='contact')
    op.drop_table('contact')