"""
Migration script to add manual price columns to assets table
Run this script to update existing databases with the new manual price fields
"""
import sqlite3
import os

def migrate_database():
    """Add manual price columns to assets table if they don't exist"""

    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'bafangce.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(assets)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add is_manually_set column
        if 'is_manually_set' not in columns:
            cursor.execute("ALTER TABLE assets ADD COLUMN is_manually_set BOOLEAN DEFAULT 0")
            print("Added is_manually_set column")
        else:
            print("is_manually_set column already exists")

        # Add manual_set_price column
        if 'manual_set_price' not in columns:
            cursor.execute("ALTER TABLE assets ADD COLUMN manual_set_price REAL")
            print("Added manual_set_price column")
        else:
            print("manual_set_price column already exists")

        # Add manual_set_at column
        if 'manual_set_at' not in columns:
            cursor.execute("ALTER TABLE assets ADD COLUMN manual_set_at DATETIME")
            print("Added manual_set_at column")
        else:
            print("manual_set_at column already exists")

        conn.commit()
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
