import sys
import asyncio

import aiohttp

USER = "user"
PASSWORD = "password"
END_POINT = "pr.oxylabs.io:7777"

# Authorizing and passing credentials along with the proxy URL 
# async def fetch():
#     async with aiohttp.ClientSession() as session:
#         proxy_auth = aiohttp.BasicAuth(USER, PASS)
#         async with session.get("http://ip.oxylabs.io", 
#             proxy="http://pr.oxylabs.io:7777", 
#             proxy_auth=proxy_auth 
#         ) as response:
#             print(await response.text())

# Passing authentication credentials in proxy URL:
 
async def fetch():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://ip.oxylabs.io", 
            proxy=f"http://{USER}:{PASSWORD}@{END_POINT}"
        ) as response: 
            print(await response.text())

if __name__ == "__main__":
    # Different Event Loop Policy must be loaded if you're using Windows OS 
    if sys.platform.startswith("win") and sys.version_info.minor >= 8:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(fetch())
