"""
Reset PostgreSQL database - Drop all tables
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

def reset_database():
    """Drop all tables from the database"""
    with connection.cursor() as cursor:
        # Get all tables
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables to drop")
        
        # Drop all tables
        for table in tables:
            table_name = table[0]
            print(f"Dropping table: {table_name}")
            cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
        
        print("\n✅ Database reset complete!")
        print("Now run: python manage.py migrate")

if __name__ == '__main__':
    confirm = input("⚠️  This will DELETE ALL DATA from the database. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        reset_database()
    else:
        print("Operation cancelled")
