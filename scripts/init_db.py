#!/usr/bin/env python
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from bifrost.core.database import db
from bifrost.core.config import get_config
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user(username: str, email: str, password: str):
    """Create an admin user in the database."""
    # Hash the password
    hashed_password = pwd_context.hash(password)
    
    # Check if user already exists
    result = db.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (username, email)
    )
    if result:
        print(f"User {username} or email {email} already exists")
        return
    
    # Create user data
    user_data = {
        'id': str(uuid.uuid4()),
        'username': username,
        'email': email,
        'password_hash': hashed_password,
        'full_name': 'Admin User',
        'department': 'Administration',
        'role': 'admin',
        'created_at': datetime.utcnow(),
        'is_active': True,
        'metadata': '{}'
    }
    
    # Add password_hash column if it doesn't exist
    db.execute("""
    ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT NOT NULL DEFAULT ''
    """)
    
    # Insert the user
    try:
        db.insert('users', user_data)
        print(f"Created admin user: {username}")
    except Exception as e:
        print(f"Error creating admin user: {e}")

def main():
    """Initialize the database and create admin user."""
    # Get admin credentials from environment or use defaults
    admin_username = os.getenv('BIFROST_ADMIN_USERNAME', 'admin')
    admin_email = os.getenv('BIFROST_ADMIN_EMAIL', 'admin@bifrost.local')
    admin_password = os.getenv('BIFROST_ADMIN_PASSWORD', 'changeme')
    
    # Create admin user
    create_admin_user(admin_username, admin_email, admin_password)
    
    print("Database initialization complete")

if __name__ == '__main__':
    main()