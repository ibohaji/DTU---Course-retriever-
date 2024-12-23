# test_firefox.py
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import os

def test_firefox():
    print("Starting Firefox test...")
    
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.binary_location = os.path.expanduser("~/firefox/firefox/firefox")
    
    print(f"Firefox binary location: {firefox_options.binary_location}")
    
    service = Service(
        executable_path=os.path.expanduser("~/firefox/geckodriver"),
        log_path=os.path.expanduser("~/firefox/geckodriver.log")
    )
    
    try:
        print("Creating Firefox driver...")
        driver = webdriver.Firefox(
            service=service,
            options=firefox_options
        )
        
        print("Getting test URL...")
        driver.get("https://kurser.dtu.dk/course/01001")
        
        print("Page title:", driver.title)
        print("Test successful!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
        
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    test_firefox()
