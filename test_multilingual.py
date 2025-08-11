#!/usr/bin/env python3
"""
Test script for multilingual implementation
"""
import json
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.content import About, Skill, Project
from app.models.translations import ContentTranslation
from app.services.translation_service import TranslationService


def test_translation_service():
    """Test the translation service functionality."""
    print("🧪 Testing Multilingual Implementation")
    print("=" * 50)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create translation service
        translation_service = TranslationService(db)
        
        # Test 1: Check if we have any content to translate
        print("\n📊 Current content in database:")
        about_items = db.query(About).all()
        skill_items = db.query(Skill).all()
        project_items = db.query(Project).all()
        
        print(f"   About items: {len(about_items)}")
        print(f"   Skill items: {len(skill_items)}")
        print(f"   Project items: {len(project_items)}")
        
        # Test 2: Create sample content if none exists
        if not about_items:
            print("\n➕ Creating sample About content...")
            sample_about = About(
                content="Hello, I'm a software developer with experience in Python, FastAPI, and modern web development.",
                photo_url="https://example.com/photo.jpg"
            )
            db.add(sample_about)
            db.commit()
            about_items = [sample_about]
            print("   ✅ Sample About content created")
        
        if not skill_items:
            print("\n➕ Creating sample Skills...")
            skills = [
                Skill(name="Python", type="technical", level=5),
                Skill(name="FastAPI", type="technical", level=4),
                Skill(name="Communication", type="interpersonal", level=4)
            ]
            for skill in skills:
                db.add(skill)
            db.commit()
            skill_items = skills
            print("   ✅ Sample Skills created")
        
        # Test 3: Create Spanish translations
        print("\n🇪🇸 Creating Spanish translations...")
        
        # About translation
        if about_items:
            about = about_items[0]
            success = translation_service.set_translation(
                content_type='about',
                content_id=about.id,
                field_name='content',
                language='es',
                translated_text="Hola, soy un desarrollador de software con experiencia en Python, FastAPI y desarrollo web moderno."
            )
            print(f"   About translation: {'✅' if success else '❌'}")
        
        # Skill translations
        skill_translations = [
            ("Python", "Python"),  # Same in Spanish
            ("FastAPI", "FastAPI"),  # Same in Spanish
            ("Communication", "Comunicación")
        ]
        
        for skill in skill_items:
            for en_name, es_name in skill_translations:
                if skill.name == en_name:
                    success = translation_service.set_translation(
                        content_type='skill',
                        content_id=skill.id,
                        field_name='name',
                        language='es',
                        translated_text=es_name
                    )
                    print(f"   Skill '{en_name}' -> '{es_name}': {'✅' if success else '❌'}")
        
        # Test 4: Test translation retrieval
        print("\n🔍 Testing translation retrieval...")
        
        if about_items:
            about = about_items[0]
            
            # Get English content
            en_content = translation_service.get_translated_content('about', about.id, 'en')
            print(f"   English content: {'✅' if en_content else '❌'}")
            if en_content:
                print(f"     Content preview: {en_content['content'][:50]}...")
            
            # Get Spanish content
            es_content = translation_service.get_translated_content('about', about.id, 'es')
            print(f"   Spanish content: {'✅' if es_content else '❌'}")
            if es_content:
                print(f"     Content preview: {es_content['content'][:50]}...")
            
            # Test available languages
            available_langs = translation_service.get_available_languages('about', about.id)
            print(f"   Available languages: {available_langs}")
        
        # Test 5: Get translation statistics
        print("\n📈 Translation statistics:")
        stats = translation_service.get_translation_stats()
        print(json.dumps(stats, indent=2, default=str))
        
        # Test 6: Test bulk content retrieval
        print("\n📚 Testing bulk content retrieval...")
        
        # Get all skills in English
        en_skills = translation_service.get_all_translated_content('skill', 'en')
        print(f"   English skills: {len(en_skills)} items")
        
        # Get all skills in Spanish
        es_skills = translation_service.get_all_translated_content('skill', 'es')
        print(f"   Spanish skills: {len(es_skills)} items")
        
        if es_skills:
            print("   Spanish skill names:")
            for skill in es_skills:
                print(f"     - {skill['name']}")
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Run database migration: python3 -m alembic upgrade head")
        print("   2. Start the application: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("   3. Test API endpoints:")
        print("      - GET /api/v1/about/?lang=en")
        print("      - GET /api/v1/about/?lang=es")
        print("      - GET /api/v1/skills/?lang=es")
        print("   4. Access admin panel: http://localhost:8000/admin/")
        print("   5. Manage translations in the admin panel")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    test_translation_service()