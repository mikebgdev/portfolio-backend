"""
Admin user setup utilities.
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.user import user_service
from app.database import SessionLocal
import os
import getpass


def create_default_admin():
    """Create default admin user if none exists."""
    db = SessionLocal()
    try:
        # Check if any admin user exists
        admin_count = db.query(User).filter(User.role == "admin").count()
        
        if admin_count == 0:
            print("No admin user found. Creating default admin user...")
            
            # Create default admin
            default_admin = user_service.create_user_with_password(
                db=db,
                email="admin@portfolio.com",
                name="Portfolio Admin", 
                password="admin123",
                role="admin"
            )
            print(f"✅ Default admin user created: {default_admin.email}")
            print("⚠️  Default password: admin123")
            print("🔐 IMPORTANT: Please change the password after first login!")
            return default_admin
        else:
            print(f"✅ Admin user(s) already exist ({admin_count} found)")
            return None
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def setup_admin_interactive():
    """Interactive admin setup for production."""
    db = SessionLocal()
    try:
        admin_count = db.query(User).filter(User.role == "admin").count()
        
        if admin_count == 0:
            print("🚀 Welcome to Portfolio Admin Setup!")
            print("No admin user found. Let's create one...\n")
            
            # Get admin details
            while True:
                email = input("📧 Admin email: ").strip()
                if "@" in email and "." in email:
                    break
                print("❌ Please enter a valid email address")
            
            name = input("👤 Admin name: ").strip() or "Portfolio Admin"
            
            # Get password
            while True:
                password = getpass.getpass("🔐 Admin password: ")
                if len(password) >= 6:
                    confirm = getpass.getpass("🔐 Confirm password: ")
                    if password == confirm:
                        break
                    else:
                        print("❌ Passwords don't match. Try again.")
                else:
                    print("❌ Password must be at least 6 characters long")
            
            # Create admin user
            admin = user_service.create_user_with_password(
                db=db,
                email=email,
                name=name,
                password=password,
                role="admin"
            )
            
            print(f"\n✅ Admin user created successfully!")
            print(f"📧 Email: {admin.email}")
            print(f"👤 Name: {admin.name}")
            print(f"\n🌐 You can now access the admin panel at: http://localhost:8000/admin/")
            
            return admin
            
        else:
            print(f"✅ Admin user(s) already exist ({admin_count} found)")
            # List existing admins
            admins = db.query(User).filter(User.role == "admin").all()
            print("📋 Existing admin users:")
            for admin in admins:
                status = "✅ Active" if admin.is_active else "❌ Inactive"
                print(f"  - {admin.email} ({admin.name}) - {status}")
            return None
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled by user")
        return None
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        db.rollback()
        return None
    finally:
        db.close()


if __name__ == "__main__":
    # Run interactive setup when called directly
    setup_admin_interactive()