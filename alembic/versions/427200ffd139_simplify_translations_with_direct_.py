"""Simplify translations with direct multilingual fields

Revision ID: 427200ffd139
Revises: update_schema_for_website
Create Date: 2025-08-11 12:10:58.505138

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '427200ffd139'
down_revision = 'update_schema_for_website'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### Data-preserving migration for About table ###
    # Add new columns as nullable first
    op.add_column('about', sa.Column('bio_en', sa.Text(), nullable=True))
    op.add_column('about', sa.Column('bio_es', sa.Text(), nullable=True))
    op.add_column('about', sa.Column('personal_statement_en', sa.Text(), nullable=True))
    op.add_column('about', sa.Column('personal_statement_es', sa.Text(), nullable=True))
    op.add_column('about', sa.Column('nationality_en', sa.String(), nullable=True))
    op.add_column('about', sa.Column('nationality_es', sa.String(), nullable=True))
    
    # Migrate existing data
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE about SET 
            bio_en = bio,
            personal_statement_en = personal_statement,
            nationality_en = COALESCE(nationality, 'Spanish'),
            nationality_es = 'Español'
        WHERE bio_en IS NULL
    """))
    
    # Make required fields NOT NULL
    op.alter_column('about', 'bio_en', nullable=False)
    op.alter_column('about', 'nationality_en', nullable=False)
    
    # Drop old columns
    op.drop_column('about', 'bio')
    op.drop_column('about', 'personal_statement')
    op.drop_column('about', 'nationality')
    # ### Contact table ###
    op.add_column('contact', sa.Column('contact_message_en', sa.Text(), nullable=True))
    op.add_column('contact', sa.Column('contact_message_es', sa.Text(), nullable=True))
    
    # Migrate contact data if contact_message exists
    connection.execute(sa.text("""
        UPDATE contact SET contact_message_en = contact_message 
        WHERE contact_message_en IS NULL AND contact_message IS NOT NULL
    """))
    
    op.drop_column('contact', 'contact_message')
    
    # ### Education table ###
    op.add_column('education', sa.Column('degree_en', sa.String(), nullable=True))
    op.add_column('education', sa.Column('degree_es', sa.String(), nullable=True))
    op.add_column('education', sa.Column('field_of_study_en', sa.String(), nullable=True))
    op.add_column('education', sa.Column('field_of_study_es', sa.String(), nullable=True))
    op.add_column('education', sa.Column('description_en', sa.Text(), nullable=True))
    op.add_column('education', sa.Column('description_es', sa.Text(), nullable=True))
    
    # Migrate education data
    connection.execute(sa.text("""
        UPDATE education SET 
            degree_en = degree,
            field_of_study_en = field_of_study,
            description_en = description
        WHERE degree_en IS NULL
    """))
    
    op.alter_column('education', 'degree_en', nullable=False)
    op.drop_column('education', 'description')
    op.drop_column('education', 'degree')
    op.drop_column('education', 'field_of_study')
    
    # ### Experience table ###
    op.add_column('experience', sa.Column('position_en', sa.String(), nullable=True))
    op.add_column('experience', sa.Column('position_es', sa.String(), nullable=True))
    op.add_column('experience', sa.Column('description_en', sa.Text(), nullable=True))
    op.add_column('experience', sa.Column('description_es', sa.Text(), nullable=True))
    
    # Migrate experience data
    connection.execute(sa.text("""
        UPDATE experience SET 
            position_en = position,
            description_en = description
        WHERE position_en IS NULL
    """))
    
    op.alter_column('experience', 'position_en', nullable=False)
    op.alter_column('experience', 'description_en', nullable=False)
    op.drop_column('experience', 'description')
    op.drop_column('experience', 'position')
    
    # ### Projects table ###
    op.add_column('projects', sa.Column('title_en', sa.String(), nullable=True))
    op.add_column('projects', sa.Column('title_es', sa.String(), nullable=True))
    op.add_column('projects', sa.Column('description_en', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('description_es', sa.Text(), nullable=True))
    
    # Migrate projects data
    connection.execute(sa.text("""
        UPDATE projects SET 
            title_en = title,
            description_en = description
        WHERE title_en IS NULL
    """))
    
    op.alter_column('projects', 'title_en', nullable=False)
    op.alter_column('projects', 'description_en', nullable=False)
    op.drop_column('projects', 'description')
    op.drop_column('projects', 'title')
    
    # ### Skills table ###
    op.add_column('skills', sa.Column('name_en', sa.String(), nullable=True))
    op.add_column('skills', sa.Column('name_es', sa.String(), nullable=True))
    
    # Migrate skills data
    connection.execute(sa.text("""
        UPDATE skills SET name_en = name WHERE name_en IS NULL
    """))
    
    op.alter_column('skills', 'name_en', nullable=False)
    op.drop_column('skills', 'name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('skills', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('skills', 'name_es')
    op.drop_column('skills', 'name_en')
    op.add_column('projects', sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('projects', sa.Column('description', sa.TEXT(), autoincrement=False, nullable=False))
    op.drop_column('projects', 'description_es')
    op.drop_column('projects', 'description_en')
    op.drop_column('projects', 'title_es')
    op.drop_column('projects', 'title_en')
    op.add_column('experience', sa.Column('position', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('experience', sa.Column('description', sa.TEXT(), server_default=sa.text("''::text"), autoincrement=False, nullable=False))
    op.drop_column('experience', 'description_es')
    op.drop_column('experience', 'description_en')
    op.drop_column('experience', 'position_es')
    op.drop_column('experience', 'position_en')
    op.add_column('education', sa.Column('field_of_study', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('education', sa.Column('degree', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('education', sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('education', 'description_es')
    op.drop_column('education', 'description_en')
    op.drop_column('education', 'field_of_study_es')
    op.drop_column('education', 'field_of_study_en')
    op.drop_column('education', 'degree_es')
    op.drop_column('education', 'degree_en')
    op.add_column('contact', sa.Column('contact_message', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('contact', 'contact_message_es')
    op.drop_column('contact', 'contact_message_en')
    op.add_column('about', sa.Column('nationality', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('about', sa.Column('personal_statement', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('about', sa.Column('bio', sa.TEXT(), autoincrement=False, nullable=False))
    op.drop_column('about', 'nationality_es')
    op.drop_column('about', 'nationality_en')
    op.drop_column('about', 'personal_statement_es')
    op.drop_column('about', 'personal_statement_en')
    op.drop_column('about', 'bio_es')
    op.drop_column('about', 'bio_en')
    # ### end Alembic commands ###