#!/usr/bin/env python3
"""
Migration script to convert existing project technologies to skills.

This script:
1. Reads existing technologies from projects
2. Creates skills for technologies that don't exist
3. Associates projects with their corresponding skills
4. Preserves backward compatibility
"""

import json
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.projects import Project
from app.models.skills import Skill, SkillCategory


def get_or_create_default_category(db):
    """Get or create a default category for migrated technologies."""
    category = db.query(SkillCategory).filter(
        SkillCategory.slug == "technologies"
    ).first()
    
    if not category:
        category = SkillCategory(
            slug="technologies",
            label_en="Technologies",
            label_es="Tecnologías",
            icon_name="mdi:code-tags",
            display_order=999,
            active=True
        )
        db.add(category)
        db.flush()
        print(f"Created default category: {category.label_en}")
    
    return category


def normalize_technology_name(tech_name: str) -> str:
    """Normalize technology name for matching."""
    return tech_name.strip().lower().replace("-", "").replace("_", "").replace(" ", "")


def get_or_create_skill(db, tech_name: str, category: SkillCategory) -> Skill:
    """Get existing skill or create new one for technology."""
    # Normalize for search
    normalized_name = normalize_technology_name(tech_name)
    
    # Try to find existing skill by normalized name
    existing_skills = db.query(Skill).all()
    for skill in existing_skills:
        if normalize_technology_name(skill.name_en) == normalized_name:
            print(f"Found existing skill for '{tech_name}': {skill.name_en}")
            return skill
    
    # Create new skill
    skill = Skill(
        name_en=tech_name.strip(),
        name_es=tech_name.strip(),  # Same name for both languages
        category_id=category.id,
        icon_name="mdi:code-tags",  # Default icon
        color="#3B82F6",  # Blue color
        display_order=0,
        active=True
    )
    db.add(skill)
    db.flush()
    print(f"Created new skill: {skill.name_en}")
    return skill


def parse_technologies(technologies_text: str) -> list:
    """Parse technologies from various formats."""
    if not technologies_text:
        return []
    
    # Try JSON first
    try:
        techs = json.loads(technologies_text)
        if isinstance(techs, list):
            return [str(tech).strip() for tech in techs if tech]
    except (json.JSONDecodeError, TypeError):
        pass
    
    # Handle comma-separated string
    if isinstance(technologies_text, str):
        return [tech.strip() for tech in technologies_text.split(",") if tech.strip()]
    
    return []


def migrate_project_technologies():
    """Main migration function."""
    db = SessionLocal()
    
    try:
        print("Starting migration of project technologies to skills...")
        
        # Get default category
        default_category = get_or_create_default_category(db)
        
        # Get all projects
        projects = db.query(Project).all()
        print(f"Found {len(projects)} projects to migrate")
        
        migrated_count = 0
        skill_cache = {}  # Cache skills to avoid duplicate queries
        
        for project in projects:
            print(f"\nMigrating project: {project.title_en}")
            
            # Skip if project already has skills
            if project.skills:
                print(f"  Project already has {len(project.skills)} skills, skipping...")
                continue
            
            # Parse technologies
            technologies = parse_technologies(project.technologies)
            if not technologies:
                print("  No technologies found, skipping...")
                continue
            
            print(f"  Found technologies: {technologies}")
            
            # Convert technologies to skills
            project_skills = []
            for tech_name in technologies:
                # Use cache to avoid duplicate queries
                cache_key = normalize_technology_name(tech_name)
                if cache_key in skill_cache:
                    skill = skill_cache[cache_key]
                else:
                    skill = get_or_create_skill(db, tech_name, default_category)
                    skill_cache[cache_key] = skill
                
                project_skills.append(skill)
            
            # Associate skills with project
            project.skills = project_skills
            print(f"  Associated {len(project_skills)} skills with project")
            
            migrated_count += 1
        
        # Commit all changes
        db.commit()
        print(f"\n✅ Migration completed successfully!")
        print(f"   - Migrated {migrated_count} projects")
        print(f"   - Created/reused {len(skill_cache)} skills")
        print(f"   - All skills assigned to category: {default_category.label_en}")
        
        # Summary
        print(f"\n📊 Summary:")
        total_projects = db.query(Project).count()
        projects_with_skills = db.query(Project).join(Project.skills).distinct().count()
        total_skills = db.query(Skill).count()
        
        print(f"   - Total projects: {total_projects}")
        print(f"   - Projects with skills: {projects_with_skills}")
        print(f"   - Total skills in database: {total_skills}")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def verify_migration():
    """Verify that migration was successful."""
    db = SessionLocal()
    
    try:
        print("\n🔍 Verifying migration...")
        
        projects = db.query(Project).all()
        for project in projects:
            if project.technologies and not project.skills:
                print(f"⚠️  Project '{project.title_en}' still has technologies but no skills")
            elif project.skills:
                skill_names = [skill.name_en for skill in project.skills]
                print(f"✅ Project '{project.title_en}' has skills: {skill_names}")
        
        print("✅ Verification completed")
        
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate project technologies to skills")
    parser.add_argument("--verify-only", action="store_true", 
                       help="Only verify migration, don't run it")
    
    args = parser.parse_args()
    
    if args.verify_only:
        verify_migration()
    else:
        migrate_project_technologies()
        verify_migration()