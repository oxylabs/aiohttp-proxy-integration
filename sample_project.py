import asyncio
import time
import sys

import aiohttp
from bs4 import BeautifulSoup
import pandas as pd

USER = "user"
PASSWORD = "pass"
END_POINT = "pr.oxylabs.io:7777"

# Generate a list of URLs to scrape
url_list = [f"https://books.toscrape.com/catalogue/category/books_1/page-{page_num}.html" \
for page_num in range(1, 51)]

async def fetch(session, sem, url):
    async with sem:
        async with session.get(url, proxy=f"http://{USER}:{PASSWORD}@{END_POINT}") as response: 
            await parse_url(await response.text())

async def parse_url(text):
    soup = BeautifulSoup(text, "lxml")
    for product_data in soup.select("ol.row > li > article.product_pod"):
        data = {
        "Title": product_data.select_one("h3 > a")["title"],
        "URL": product_data.select_one("h3 > a").get("href")[5:],
        "Product Price": product_data.select_one("p.price_color").text,
        "Stars": product_data.select_one("p")["class"][1],
        }
        full_data.append(data)
        print(f"Grabbing book: {data['Title']}")
    
async def create_jobs():
    full_data = []
    sem = asyncio.Semaphore(4)
    async with aiohttp.ClientSession() as session:
        get_results = await asyncio.gather(*[fetch(session, sem, url) for url in url_list])

if __name__ == "__main__":
    start = time.time()
    # Different Event Loop Policy must be loaded if you're using Windows OS
    if sys.platform.startswith("win") and sys.version_info.minor >= 8:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(create_jobs())
    
    print(f"Total of {len(full_data)} products gathered in {time.time() - start} seconds")
    df = pd.DataFrame(full_data)
    df["URL"] = df["URL"].map(lambda x: ''.join(["https://books.toscrape.com/catalogue", x]))
    df.to_csv("scraped-books.csv", encoding='utf-8-sig', index=False)
