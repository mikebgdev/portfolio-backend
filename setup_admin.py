#!/usr/bin/env python3
"""
Portfolio Admin Setup Script

Run this script to set up the initial admin user.
"""

if __name__ == "__main__":
    from app.utils.admin_setup import setup_admin_interactive
    setup_admin_interactive()