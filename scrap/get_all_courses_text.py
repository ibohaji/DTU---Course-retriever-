from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import json
import time
from tqdm import tqdm
import os
import shutil
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(filename='process.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.binary_location = os.path.expanduser("~/firefox/firefox/firefox")
    
    service = Service(
        executable_path=os.path.expanduser("~/firefox/geckodriver"),
        log_path=os.path.expanduser("~/firefox/geckodriver.log")
    )
    
    driver = webdriver.Firefox(service=service, options=firefox_options)
    
    try:
        driver.get(url)
        time.sleep(0.5)
        return extract_content_from_html(driver.page_source)
    finally:
        driver.quit()

def fetch_course_details(course):
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
        return enriched_course
    except Exception as e:
        logging.error(f"Error processing {course['course_url']}: {str(e)}")
        print(f"Error processing {course['course_url']}: {str(e)}")  # Print error to console
        raise e

def process_all_courses():
    # Load existing courses
    with open('courses.json', 'r', encoding='utf-8') as f:
        courses = json.load(f)
    
    # Load existing enriched courses if the file exists
    enriched_courses = []
    if os.path.exists('courses_with_details.json'):
        try:
            with open('courses_with_details.json', 'r', encoding='utf-8') as f:
                if os.path.getsize('courses_with_details.json') > 0:  # Check if file is not empty
                    enriched_courses = json.load(f)
        except json.JSONDecodeError:
            print("Warning: courses_with_details.json is not a valid JSON file. Starting fresh.")
    
    # Determine the starting index based on the length of enriched_courses
    start_index = len(enriched_courses)
    remaining_courses = courses[start_index:]
    
    # Process each course with a progress bar
    print(f"\nContinuing processing from course {start_index + 1} of {len(courses)}:")
    for i, course in enumerate(tqdm(remaining_courses)):
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
            
            # Save to a temporary file every 25 courses
            current_index = start_index + i + 1
            if current_index % 25 == 0:
                with open('courses_with_details_temp.json', 'w', encoding='utf-8') as f:
                    json.dump(enriched_courses, f, ensure_ascii=False, indent=2)
                shutil.move('courses_with_details_temp.json', 'courses_with_details.json')
                print(f"\nProgress saved: {current_index} courses processed")
            
        except Exception as e:
            print(f"\nError processing {course['course_url']}: {str(e)}")
            enriched_courses.append(course)
    
    # Save final result to a temporary file and then move it
    with open('courses_with_details_temp.json', 'w', encoding='utf-8') as f:
        json.dump(enriched_courses, f, ensure_ascii=False, indent=2)
    shutil.move('courses_with_details_temp.json', 'courses_with_details.json')
    
    print("\nProcessing complete! Saved to courses_with_details.json")

def main():
    process_all_courses()

if __name__ == "__main__":
    main()
