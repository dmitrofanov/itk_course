import asyncio
import aiohttp
import aiofiles
import json

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url"
]

async def make_request(session: aiohttp.ClientSession, url: str, sem: asincio.Semaphore):
    async with sem:
        try:
            async with session.get(url) as resp:
                return url, resp.status
        except aiohttp.client_exceptions.ClientConnectorDNSError:
            return url, 0


async def fetch_urls(urls: list[str], file_path: str):
    async with aiofiles.open(file_path, 'w') as file:
        await file.write('')
    limit = asyncio.Semaphore(5)
    async with aiohttp.ClientSession() as session:
        tasks = [make_request(session, url, limit) for url in urls]
        results = await asyncio.gather(*tasks)

    data = [
        {
            'url': url,
            'status_code': status_code
        }
        for url, status_code in results
    ]
    for item in data:
        async with aiofiles.open(file_path, 'a') as file:
            await file.write(json.dumps(item) + '\n')


if __name__ == '__main__':
    asyncio.run(fetch_urls(urls, './results.jsonl'))
