import time
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver

browser = webdriver.Firefox()
browser.execute_script(f'''window.location.assign("https://divar.ir/s/marivan/car")''')

days_input = """How many days?
امروز: 0
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
motors = []
bodies = []
failed_requests = []
counter = start_index = 0


async def get_pages(session, link):
    global counter
    local_counter = counter
    counter += 1
    print('getting link: ', counter)
    async with session.get(link) as page:
        text = await page.read()
        if page.status != 200:
            failed_requests.append(link[16:])
            return
        soup = BeautifulSoup(text.decode('utf-8'), 'html5lib')
        rows = soup.find_all('div', {'class': 'kt-base-row kt-base-row--large kt-unexpandable-row'})

        for row in rows:
            title = row.find('p', {'class': 'kt-base-row__title kt-unexpandable-row__title'})
            value = row.find('p', {'class': 'kt-unexpandable-row__value'})

            if title and value:
                if 'وضعیت موتور' in title.text and 'نیاز به تعمیر' in value.text:
                    motors.append(link)
                elif 'وضعیت بدنه' in title.text and 'تصادفی' in value.text:
                    bodies.append(link)

    print('finished link: ', local_counter + 1)


def asyncro(hrefs):
    async def async_requests(loop):
        global counter
        tasks = list()
        async with aiohttp.ClientSession(loop=loop) as session:
            for href in hrefs:
                link = f'https://divar.ir{href}'
                tasks.append(get_pages(session, link))
            grouped_tasks = asyncio.gather(*tasks)
            return await grouped_tasks

    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_requests(loop))


def func():
    global hrefs
    global start_index
    while True:
        soup = BeautifulSoup(browser.page_source, 'lxml')
        for element in soup.find_all('div', {'class': 'post-card-item-af972'}):
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
        browser.execute_script("window.scrollBy(0, 150)")
        asyncro(hrefs[start_index:])
        if start_index == len(hrefs):
            time.sleep(1)
        else:
            start_index = len(hrefs)


if __name__ == '__main__':
    func()

    while failed_requests:  # failed requests here will be requested again
        new, failed_requests = failed_requests, []
        asyncro(new)

    print(f'Count all Hrefs: {len(hrefs)}')
    print(f'Count all motors: {len(motors)}')
    print(f'Count all bodies: {len(bodies)}')

    motors.extend(bodies)
    for link in motors:
        browser.execute_script(f'''window.open("{link}", "_blank");''')
        time.sleep(2)

