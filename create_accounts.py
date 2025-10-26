#!/usr/bin/env python3
"""
Helper script to create test accounts in the database.
This avoids hardcoding credentials in the application source code.
"""

import sqlite3
import hashlib
import json
import sys
from pathlib import Path


def create_accounts(accounts_file='test_accounts.json', db_file='users.db'):
    """Create user accounts from a JSON configuration file."""
    
    # Load account configuration
    accounts_path = Path(accounts_file)
    if not accounts_path.exists():
        print(f"❌ Error: {accounts_file} not found")
        sys.exit(1)
    
    with open(accounts_path) as f:
        config = json.load(f)
    
    accounts = config.get('accounts', [])
    if not accounts:
        print("❌ Error: No accounts found in configuration file")
        sys.exit(1)
    
    # Connect to database
    db = sqlite3.connect(db_file)
    db.row_factory = sqlite3.Row
    
    print(f"📁 Creating accounts in {db_file}...")
    print()
    
    # Clear existing users
    db.execute('DELETE FROM users')
    print("🗑️  Cleared existing users")
    
    # Create each account
    for account in accounts:
        username = account['username']
        password = account['password']
        role = account['role']
        user_id = account.get('user_id')
        
        # Hash password (using MD5 to match app's vulnerable implementation)
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        # Default contact info
        email = f"{username}@company.com"
        phone = "123-456-7890" if role == "admin" else "098-765-4321"
        address = f"123 {username.title()} Street, City, 12345"
        
        # Insert user
        db.execute(
            'INSERT INTO users (id, username, password, role, email, phone, address) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (user_id, username, password_hash, role, email, phone, address)
        )
        
        print(f"✅ Created {role:5} account: {username:10} (ID: {user_id}, password: {password})")
    
    db.commit()
    db.close()
    
    print()
    print(f"✅ Successfully created {len(accounts)} accounts")
    print(f"📝 Credentials are in {accounts_file}")
    

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Create test accounts for vulnerable app')
    parser.add_argument('--accounts', default='test_accounts.json', 
                       help='Path to accounts JSON file (default: test_accounts.json)')
    parser.add_argument('--db', default='users.db',
                       help='Path to database file (default: users.db)')
    
    args = parser.parse_args()
    
    create_accounts(args.accounts, args.db)
