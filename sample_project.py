import asyncio
import time
import sys
import os

from bs4 import BeautifulSoup
import pandas as pd
import aiohttp

USER = "user"
PASSWORD = "pass"
END_POINT = "pr.oxylabs.io:7777"

# Generate a list of URLs to scrape
url_list = [
f"https://books.toscrape.com/catalogue/category/books_1/page-{page_num}.html" 
for page_num 
in range(1, 51)
]

async def fetch(session, sem, url):
        async with sem:
            async with session.get(url, 
                proxy=f"http://{USER}:{PASSWORD}@{END_POINT}"
            ) as response:
                await parse_url(await response.text())

async def parse_url(text):
    soup = BeautifulSoup(text, "lxml")
    for product_data in soup.select("ol.row > li > article.product_pod"):
        data = {
            "title": product_data.select_one("h3 > a")["title"],
            "url": product_data.select_one("h3 > a").get("href")[5:],
            "product_price": product_data.select_one("p.price_color").text,
            "stars": product_data.select_one("p")["class"][1],
        }
        final_list.append(data)
        print(f"Grabing book: {data['title']}")
    
async def create_jobs():
    final_res = []
    sem = asyncio.Semaphore(4)
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[fetch(session, sem, url) 
        for url in url_list
        ])
        
if __name__ == "__main__":
    final_list = []
    start = time.perf_counter()
    # Different Event Loop Policy must be loaded if you're using Windows OS to avoid "Event Loop is closed"
    if sys.platform.startswith("win") and sys.version_info.minor >= 8:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
      asyncio.run(create_jobs())   
    except Exception: 
        print("We broke, but there might still be some results")
    
    print(f"\nTotal of {len(final_list)} products gathered in {time.perf_counter() - start:.2f} seconds")
    df = pd.DataFrame(final_list)
    df["url"] = df["url"].map(lambda x: ''.join(["https://books.toscrape.com/catalogue", x]))
    filename = "scraped-books.csv"
    df.to_csv(filename, encoding='utf-8-sig', index=False)
    print(f"\nExtracted data can be accessed at {os.path.join(os.getcwd(), filename)}")