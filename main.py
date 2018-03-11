import re
import signal

import sys
from fake_useragent import UserAgent
import asyncio
import aiohttp


NUMBER_OF_CONCURRENT_TASKS = 1
# in seconds (floating point)
SLEEP_TIME = 1


async def try_to_search(session):
    headers = {
        'User-Agent': UserAgent().random
    }
    search_text = 'list comprehension'

    url = 'https://www.google.com/search?client=ubuntu&q={}&oq={}'.format(search_text, search_text)
    async with session.get(url, headers=headers) as resp:
        resp_text = await resp.text()

        matches = re.search(r'(https?://(www.)?google.com/foobar/[^\"]+)', resp_text)
        if matches:
            print(matches.groups()[0])
            sys.stdout.flush()
            return True

    return False


tries = 0
successful = 0


async def main():
    global tries, successful

    async with aiohttp.ClientSession() as session:
        while True:
            if await try_to_search(session):
                successful += 1
            tries += 1
            await asyncio.sleep(SLEEP_TIME)


def exit_handler(*_):
    global tries, successful
    print(' tries: {}; successful: {}'.format(tries, successful))
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_handler)
    asyncio.get_event_loop().run_until_complete(main())
