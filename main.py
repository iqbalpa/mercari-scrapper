import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MERCARI_JOB_LINK = "https://careers.mercari.com/job-categories/engineering/"

def get_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(options=options)
    return driver

def extract_job_info(driver, title, job_link):
    job_info = {}
    try:
        # redirect to the apply page
        driver.get(job_link)
        # wait until the page is fully loaded
        timeout = 10
        try:
            span_present = EC.presence_of_element_located((By.TAG_NAME, 'span'))
            WebDriverWait(driver, timeout).until(span_present)
        except TimeoutException:
            logger.warning(f"Timed out waiting for page to load: {job_link}")
            return None
        # create job info dictionary
        job_info["Role Title"] = title
        job_info["Link"] = job_link
        span_elements = driver.find_elements(By.TAG_NAME, 'span')
        for span in span_elements:
            html = span.get_attribute("outerHTML")
            attr = span.get_attribute("data-ui")
            if attr is None:
                continue
            soup = BeautifulSoup(html, "html.parser")
            try:
                job_info[attr] = soup.strong.text
            except:
                job_info[attr] = soup.text
        logger.info(f"Extracted job info for: {title}")
        return job_info
    except Exception as e:
        logger.error(f"Error extracting job info: {e}")
        return None

def main():
    driver = get_driver()
    driver.get(MERCARI_JOB_LINK)
    logger.info(f"Access site: {driver.title}")

    li_elements = driver.find_elements(By.XPATH, "//li[@class='job-list__item']")
    logger.info(f"Found {len(li_elements)} job elements")

    # extract the job title and link
    lst_job = []
    for i, element in enumerate(li_elements):
        element = element.get_attribute("outerHTML")
        soup = BeautifulSoup(element, "html.parser")
        role_title = soup.li.a.h4.text
        link = soup.find("a", href=True)["href"]
        lst_job.append({
            "title": role_title,
            "link": link
        })
    logger.info(f"Got all job links. Total links: {len(lst_job)}")

    result = []
    for i, job in enumerate(lst_job):
        logger.info(f"Processing job {i+1} of {len(lst_job)}")
        job_info = extract_job_info(driver, job["title"], job["link"])
        if job_info:
            result.append(job_info)
        time.sleep(3)  # Small delay to avoid server overload
        if i==2: break
    
    driver.quit()
    logger.info(f"Finished processing all jobs. Total jobs extracted: {len(result)}")
    print(result)

if __name__ == "__main__":
    main()