import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

browser = webdriver.Firefox()
browser.get('https://divar.ir/s/marivan/auto')
# url = input('Please Enter the Url: ') or 'https://divar.ir/s/kurdistan-province/auto'

days_input = """How many days?
دیروز: 1
پریروز: 2
۳ روز: 3
....
: """
days = int(input(days_input))
if days > 3:
    browser.close()
    raise ValueError('Wrong days number')
date = {
    'دیروز': 1,
    'پریروز': 2,
    '۳ روز': 3,
}

hrefs = []


def func():
    global hrefs
    while True:
        soup = BeautifulSoup(browser.page_source, 'lxml')
        for element in soup.find_all('div', {'class': 'post-card-item'}):
            try:
                date_text = element.find('span', 'kt-post-card__bottom-description kt-text-truncate').text
                for key in date.keys():
                    if key in date_text and date[key] > days:
                        return True
                a = element.find('a')
                href = a['href']
                if href not in hrefs:
                    hrefs.append(href)
            except Exception:
                pass
        browser.execute_script("window.scrollBy(0, 500)")
        time.sleep(2)


func()
print(f'Count all Hrefs: {len(hrefs)}')
motors = []
bodies = []

for href in hrefs:
    link = f'https://divar.ir{href}'
    print(link)
    page_content = requests.get(link).content
    soup = BeautifulSoup(page_content, 'lxml')
    rows = soup.find_all('div', {'class': 'kt-base-row kt-base-row--large kt-unexpandable-row'})
    for row in rows:
        title = row.find('p', {'class': 'kt-base-row__title kt-unexpandable-row__title'})
        value = row.find('p', {'class': 'kt-unexpandable-row__value'})
        if 'وضعیت موتور' in title.text:
            if 'نیاز به تعمیر' in value.text:
                motors.append(link)
        elif 'وضعیت بدنه' in title.text:
            if 'تصادفی' in value.text:
                bodies.append(link)

print(f'Count all motors: {len(motors)}')
print(f'Count all bodies: {len(bodies)}')

motors.extend(bodies)
for link in motors:
    # browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.COMMAND + 't')
    browser.execute_script(f'''window.open("{link}", "_blank");''')
    time.sleep(2)


# with open('cars.txt', 'w', encoding='utf-8') as file:
#     motors.extend(body)
#     for link in motors:
#         file.write(f'{link},\n')
#         browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.COMMAND + 't')
#     for link in body:
#         file.write(f',{link}\n')
