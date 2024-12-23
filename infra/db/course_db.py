import sqlite3
from pathlib import Path

class CourseDB:
    def __init__(self):
        current_dir = Path(__file__).parent.parent.parent
        self.db_path = current_dir / "data/courses.db"

    def get_course(self, course_number: str) -> dict:
        """Get a single course by its number."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM courses WHERE course_number = ?
        ''', (course_number,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'course_number': result[0],
                'course_name': result[1],
                'course_url': result[2],
                'details': result[3],
                'level': result[4],
                'general_course_objectives': result[5],
                'learning_objectives': result[6],
                'content': result[7]
            }
        return None

    def search_courses(self, keyword: str, limit: int = 10) -> list[dict]:
        """Search courses by keyword in name or content."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM courses 
        WHERE course_name LIKE ? OR content LIKE ? OR learning_objectives LIKE ?
        LIMIT ?
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'course_number': row[0],
            'course_name': row[1],
            'course_url': row[2],
            'details': row[3],
            'level': row[4],
            'general_course_objectives': row[5],
            'learning_objectives': row[6],
            'content': row[7]
        } for row in results]

    def get_courses_by_level(self, level: str) -> list[dict]:
        """Get all courses for a specific level (BSc, MSc, etc)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM courses WHERE level = ?', (level,))
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'course_number': row[0],
            'course_name': row[1],
            'course_url': row[2],
            'details': row[3],
            'level': row[4],
            'general_course_objectives': row[5],
            'learning_objectives': row[6],
            'content': row[7]
        } for row in results] 