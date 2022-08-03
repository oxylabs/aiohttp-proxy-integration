# Integrating Oxylabs' Residential Proxies with AIOHTTP
[<img src="https://img.shields.io/static/v1?label=&message=Python&color=brightgreen" />](https://github.com/topics/python) 
[<img src="https://img.shields.io/static/v1?label=&message=Web%20Scraping&color=important" />](https://github.com/topics/web-scraping) 
[<img src="https://img.shields.io/static/v1?label=&message=Residential%20Proxy&color=blueviolet" />](https://github.com/topics/residential-proxy) 
[<img src="https://img.shields.io/static/v1?label=&message=Aiohttp&color=blue" />](https://github.com/topics/aiohttp) 
[<img src="https://img.shields.io/static/v1?label=&message=Asyncio&color=yellow" />](https://github.com/topics/asyncio)

## Requirements for the Integration

For the integration to work you'll need to install `aiohttp` library, use `Python 3.6` 
version or higher and Residential Proxies. <br> If you don't have `aiohttp` library, 
you can install it by using `pip` command:

```bash 
pip install aiohttp
```

You can get Residential Proxies here: https://oxy.yt/arWH

## Proxy Authentication

There are 2 ways to authenticate proxies with `aiohttp`.<br>
The first way is to authorize and pass credentials along with the proxy URL
using `aiohttp.BasicAuth`:

```python
import aiohttp

USER = "user"
PASSWORD = "pass"
END_POINT = "pr.oxylabs.io:7777"
 
async def fetch():
    async with aiohttp.ClientSession() as session:
        proxy_auth = aiohttp.BasicAuth(USER, PASSWORD)
        async with session.get(
                "http://ip.oxylabs.io", 
                proxy="http://pr.oxylabs.io:7777", 
                proxy_auth=proxy_auth ,
        ) as resp:
            print(await resp.text())
```

The second one is by passing authentication credentials in proxy URL:

```python
import aiohttp

USER = "user"
PASSWORD = "pass"
END_POINT = "pr.oxylabs.io:7777"

async def fetch():
    async with aiohttp.ClientSession() as session:
        async with session.get(
                "http://ip.oxylabs.io", 
                proxy=f"http://{USER}:{PASSWORD}@{END_POINT}",
        ) as resp: 
            print(await resp.text())
```

In order to use your own proxies, adjust `user` and `pass` fields with your 
Oxylabs account credentials.

## Testing Proxies

To see if the proxy is working, try visiting https://ip.oxylabs.io. 
If everything is working correctly, it will return an IP address of a proxy 
that you're currently using.

## Sample Project: Extracting Data From Multiple Pages

To better understand how residential proxies can be utilized for asynchronous 
data extracting operations, we wrote a sample project to scrape product listing 
data and save the output to a `CSV` file. The proxy rotation allows us to send 
multiple requests at once risk-free – meaning that we don't need to worry about 
CAPTCHA or getting blocked. This makes the web scraping process extremely fast 
and efficient – now you can extract data from thousands of products in a matter 
of seconds!

```python
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
```

If you want to test the project's script by yourself, you'll need to install 
some additional packages. To do that, simply download `requirements.txt` file 
and use `pip` command:

```bash 
pip install -r requirements.txt
```

If you're having any trouble integrating proxies with `aiohttp` and this guide 
didn't help you - feel free to contact Oxylabs customer support at support@oxylabs.io.
