import json
import sqlite3
from pathlib import Path
import os

def init_course_db():
    # Get path to the JSON file and database
    current_dir = Path(__file__).parent.parent.parent
    json_path = "courses_with_details_new_temp.json"
    
    # Create a data directory in the current working directory for the database
    data_dir = current_dir / "data"
    data_dir.mkdir(exist_ok=True)  # Create the directory if it doesn't exist
    
    db_path = data_dir / "courses.db"
    
    print(f"Creating database at: {db_path}")
    print(f"Reading JSON from: {json_path}")

    # Create/connect to SQLite database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create the courses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            course_number TEXT PRIMARY KEY,
            course_name TEXT,
            course_url TEXT,
            details TEXT,
            level TEXT,
            general_course_objectives TEXT,
            learning_objectives TEXT,
            content TEXT
        )
        ''')

        # Load and insert the JSON data
        with open(json_path, 'r') as f:
            courses = json.load(f)
            
        print(f"Loaded {len(courses)} courses from JSON")

        # Insert data
        for course in courses:
            cursor.execute('''
            INSERT OR REPLACE INTO courses VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                course['course_number'],
                course['course_name'],
                course['course_url'],
                course['details'],
                course['level'],
                course["general_course_objectives"],  # Using get() to handle missing fields
                course["learning_objectives"],  # Using get() to handle missing fields
                course["content"]

            ))

        conn.commit()
        print("Database created successfully!")
        
    except sqlite3.OperationalError as e:
        print(f"Error creating database: {e}")
        print(f"Please ensure you have write permissions in: {data_dir}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    init_course_db() 