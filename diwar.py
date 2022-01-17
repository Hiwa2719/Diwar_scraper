import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

browser = webdriver.Firefox()

url = 'https://divar.ir/s/tehran/car'

browser.get(url)

# soup = BeautifulSoup(browser.page_source, 'lxml')

# table = soup.find('table', class_='chart')
count = 0
hrefs = []
for _ in range(30):
    browser.execute_script("window.scrollBy(0, 500)")
    for element in browser.find_elements(By.CLASS_NAME, 'post-card-item'):
        try:
            a = element.find_element(By.CSS_SELECTOR, 'a')
            href = a.get_attribute('href')
            if href not in hrefs:
                hrefs.append(href)
        except Exception:
            count += 1
    time.sleep(2)

print(hrefs)
