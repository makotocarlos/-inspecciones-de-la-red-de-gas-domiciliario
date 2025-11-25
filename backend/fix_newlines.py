"""
Fix files with escaped newlines
"""
import os
import re

def fix_file(filepath):
    """Fix a file with escaped newlines"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has escaped newlines at the start
        if content.startswith('\\') or content.startswith('""\"\\n'):
            print(f"Fixing {filepath}")
            # Remove escaped characters and fix
            fixed = content.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed)
            return True
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
    return False

def main():
    """Main function"""
    fixed_count = 0
    
    # List of files that might have issues
    files_to_check = [
        'dashboard/admin.py',
        'dashboard/urls.py',
        'dashboard/views.py',
        'notifications/admin.py',
        'notifications/urls.py',
        'notifications/serializers.py',
        'notifications/views.py',
        'reports/admin.py',
        'reports/urls.py',
        'reports/serializers.py',
        'reports/views.py',
    ]
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            if fix_file(filepath):
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()
