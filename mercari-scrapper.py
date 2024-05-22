from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# initiate driver
driver = webdriver.Chrome()

# get the website
driver.get("https://careers.mercari.com/job-categories/engineering/")
print(f"\n========== {driver.title} ==========")

# find the list of <li> elements
li_elements = driver.find_elements(By.XPATH, "//li[@class='job-list__item']")

# get the html form of elements
html_contents = []
for element in li_elements:
    html_content = element.get_attribute("outerHTML")
    html_contents.append(html_content)

# iterate over list of jobs
for i, html in enumerate(html_contents):
    # initiate beautifulsoup object
    soup = BeautifulSoup(html, 'html.parser')
    # get the role title
    role_title = soup.li.a.h4.text
    # get the link for apply this role
    link = soup.find("a", href=True)["href"]

    # * redirect to the apply page
    driver.get(link)
    print(driver.title)
    timeout = 10
    try:
        span_present = EC.presence_of_element_located((By.TAG_NAME, 'span'))
        WebDriverWait(driver, timeout).until(span_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
    
    dict_info = {
        "title": role_title,
        "link": link,
    }
    span_elements = driver.find_elements(By.TAG_NAME, 'span')
    for span in span_elements:
        html = span.get_attribute("outerHTML")
        attr = span.get_attribute("data-ui")
        if attr is None:
            continue
        soup = BeautifulSoup(html, "html.parser")
        try:
            dict_info[attr] = soup.strong.text
        except:
            dict_info[attr] = soup.text
    print(dict_info)
    break

driver.quit()