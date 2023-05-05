import aiohttp
import asyncio
import logging
import re
from Models import Models

CAT_URL = 'https://www.rubylane.com/search'

HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "Referer": "https://www.rubylane.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }


async def fetch_cat_url() -> str:
    session_timeout = aiohttp.ClientTimeout(total=600)
    try:
        async with aiohttp.ClientSession(headers=HEADERS, timeout=session_timeout) as session:
            async with session.get(url=CAT_URL) as double_resp:
                print(double_resp.status)
                return await double_resp.text()
    except Exception as error:
        logging.warning(error)
        await asyncio.sleep(0.1)


async def parse_cat_urls(html: str) -> [str]:
    regexp = r'Filter by.*small>'
    return re.findall(regexp, html)


async def convert_categories_data(objects: [str]) -> [Models.Category]:
    categories = []
    key_re = r'data-key=\"(.*)\">'
    href_re = r'href=\"(.*)\" c'
    objects_count_re = r'll\>(.*)\<\/'

    for category_object in objects:
        try:
            key_data = re.findall(key_re, category_object)[0]
            href_data = re.findall(href_re, category_object)[0]
            count_data = re.findall(objects_count_re, category_object)[0]
            count = int(re.sub(',', '', count_data))
            new_model = Models.Category(key=key_data, href=href_data, objects_count=count)
            categories.append(new_model)
        except Exception as error:
            logging.warning(error)
            continue
    return categories


async def main():
    html = await fetch_cat_url()
    categories_str = await parse_cat_urls(html)
    categories_obj = await convert_categories_data(categories_str)
    count_objects = sum(c.objects_count for c in categories_obj)
    logging.info("parsed, total objects: ", count_objects)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()

