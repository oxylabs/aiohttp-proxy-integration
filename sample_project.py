import asyncio
import time
import sys
import os

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

USER = "user"
PASSWORD = "pass"
END_POINT = "pr.oxylabs.io:7777"

# Generate a list of URLs to scrape.
url_list = [
    f"https://books.toscrape.com/catalogue/category/books_1/page-{page_num}.html"
    for page_num in range(1, 51)
]


async def parse_data(text, results_list):
    soup = BeautifulSoup(text, "lxml")
    for product_data in soup.select("ol.row > li > article.product_pod"):
        data = {
            "title": product_data.select_one("h3 > a")["title"],
            "url": product_data.select_one("h3 > a").get("href")[5:],
            "product_price": product_data.select_one("p.price_color").text,
            "stars": product_data.select_one("p")["class"][1],
        }
        results_list.append(data)  # Fill results_list by reference.
        print(f"Extracted data for a book: {data['title']}")


async def fetch(session, sem, url, results_list):
    async with sem:
        async with session.get(
            url,
            proxy=f"http://{USER}:{PASSWORD}@{END_POINT}",
        ) as response:
            await parse_data(await response.text(), results_list)


async def create_jobs(results_list):
    sem = asyncio.Semaphore(4)
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[fetch(session, sem, url, results_list) for url in url_list]
        )


if __name__ == "__main__":
    results = []
    start = time.perf_counter()

    # Different EventLoopPolicy must be loaded if you're using Windows OS.
    # This helps to avoid "Event Loop is closed" error.
    if sys.platform.startswith("win") and sys.version_info.minor >= 8:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(create_jobs(results))
    except Exception as e:
        print(e)
        print("We broke, but there might still be some results")

    print(
        f"\nTotal of {len(results)} products from {len(url_list)} pages "
        f"gathered in {time.perf_counter() - start:.2f} seconds.",
    )
    df = pd.DataFrame(results)
    df["url"] = df["url"].map(
        lambda x: "".join(["https://books.toscrape.com/catalogue", x])
    )
    filename = "scraped-books.csv"
    df.to_csv(filename, encoding="utf-8-sig", index=False)
    print(f"\nExtracted data can be found at {os.path.join(os.getcwd(), filename)}")
