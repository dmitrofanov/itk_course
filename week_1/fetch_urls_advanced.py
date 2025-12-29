import asyncio
import aiohttp
import aiofiles
import json

urls = [line for line in open('urls.txt')]

async def process_url(session: aiohttp.ClientSession, url: str, sem: asincio.Semaphore, file_path: str):
    async with sem:
        try:
            await asyncio.sleep(2)
            async with session.get(url) as resp:
                content = await resp.json()
        except aiohttp.client_exceptions.ClientConnectorDNSError:
            content = {}

        data = {
            'url': url,
            'content': content
        }
        async with aiofiles.open(file_path, 'a') as file:
            await file.write(json.dumps(data) + '\n')


async def fetch_urls(urls: list[str], file_path: str):
    async with aiofiles.open(file_path, 'w') as file:
        await file.write('')
    limit = asyncio.Semaphore(5)
    async with aiohttp.ClientSession() as session:
        tasks = (process_url(session, url, limit, file_path) for url in urls)
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(fetch_urls(urls, './results.json'))
