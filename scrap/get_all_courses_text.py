from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import time
from tqdm import tqdm
import requests

def extract_content_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the second column that contains our target content
    content_column = soup.find_all('div', class_='col-md-6 col-sm-12 col-xs-12')[1]
    content_box = content_column.find('div', class_='box')
    
    details = {
        'general_course_objectives': '',
        'learning_objectives': '',
        'content': ''
    }
    
    # Find all sections
    sections = content_box.find_all('div', class_='bar')
    
    for section in sections:
        section_title = section.text.strip().lower()
        
        # Get the content after this section until the next section
        content = []
        for sibling in section.next_siblings:
            if sibling.name == 'div' and 'bar' in sibling.get('class', []):
                break
            if sibling.string and sibling.string.strip():
                content.append(sibling.string.strip())
            elif sibling.name == 'ul':  # Handle bullet points
                for li in sibling.find_all('li'):
                    content.append(f"• {li.text.strip()}")
        
        # Store the content in the appropriate key
        if 'general course objectives' in section_title:
            details['general_course_objectives'] = '\n'.join(content)
        elif 'learning objectives' in section_title:
            details['learning_objectives'] = '\n'.join(content)
        elif 'content' in section_title:
            details['content'] = '\n'.join(content)
    
    return details

def get_course_details(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://kurser.dtu.dk/',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
    }
    
    print(f"\nFetching {url}")
    response = requests.get(url, headers=headers)
    print(f"Response status code: {response.status_code}")
    print(f"Response URL: {response.url}")
    
    # Save the response to a file
    with open('response_course.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("\nSaved response to response_course.html")
    
    return None

def process_all_courses():
    # Load existing courses
    with open('courses.json', 'r', encoding='utf-8') as f:
        courses = json.load(f)
    
    # Create a new list for courses with details
    enriched_courses = []
    
    # Process each course with a progress bar
    print(f"\nProcessing {len(courses)} courses:")
    for i, course in enumerate(tqdm(courses)):
        try:
            # Get additional details
            details = get_course_details(course['course_url'])
            
            # Combine original course data with new details
            enriched_course = {
                **course,
                'general_course_objectives': details['general_course_objectives'],
                'learning_objectives': details['learning_objectives'],
                'content': details['content']
            }
            
            enriched_courses.append(enriched_course)
            
            # Save to main output file every 25 courses
            if (i + 1) % 25 == 0:
                with open('courses_with_details.json', 'w', encoding='utf-8') as f:
                    json.dump(enriched_courses, f, ensure_ascii=False, indent=2)
                print(f"\nProgress saved: {i+1} courses processed")
            
        except Exception as e:
            print(f"\nError processing {course['course_url']}: {str(e)}")
            enriched_courses.append(course)
    
    # Save final result
    with open('courses_with_details.json', 'w', encoding='utf-8') as f:
        json.dump(enriched_courses, f, ensure_ascii=False, indent=2)
    
    print("\nProcessing complete! Saved to courses_with_details.json")

def main():
    # Load courses
    with open('courses.json', 'r', encoding='utf-8') as f:
        courses = json.load(f)
    
    # Test with first course
    test_course = courses[0]
    details = get_course_details(test_course['course_url'])

if __name__ == "__main__":
    main()