import requests
import json
from bs4 import BeautifulSoup

def parse_course_row(row):
    """Parse a single course row and extract relevant information"""
    try:
        course_cell = row.find_all('td')[1]
        if not course_cell:
            return None
            
        # Get course link
        course_link = course_cell.find('a')
        if not course_link:
            return None
            
        details = course_cell.find('small')
        details_text = details.text.strip() if details else ""
        
        course_text = course_link.text.strip()
        course_number = course_text.split(' - ')[0].strip()
        course_name = course_text.split(' - ')[1].strip() if ' - ' in course_text else ""
        
        level_cell = row.find_all('td')[2]
        level = level_cell.text.strip() if level_cell else ""
        
        return {
            'course_number': course_number,
            'course_name': course_name,
            'course_url': 'https://kurser.dtu.dk' + course_link['href'],
            'details': details_text,
            'level': level
        }
    except Exception as e:
        print(f"Error parsing row: {e}")
        return None

try:
    with open('response.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    table = soup.find('table', class_='table')
    
    courses = []
    if table:
        # Get all rows
        rows = table.find_all('tr')
        
        # Process each row
        for row in rows:
            # Skip department header rows
            if row.find('td', attrs={'colspan': '3'}):
                continue
                
            course_data = parse_course_row(row)
            if course_data:
                courses.append(course_data)
    
    # Save to JSON file
    with open('courses.json', 'w', encoding='utf-8') as f:
        json.dump(courses, f, indent=4, ensure_ascii=False)

except Exception as e:
    print(f"Error: {e}")

