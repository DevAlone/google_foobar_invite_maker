from fake_useragent import UserAgent

import ssl
import time
import asyncio
import aiohttp
import argparse
import re
import signal
import sys


NUMBER_OF_CONCURRENT_TASKS = 1
# in seconds (floating point)
SLEEP_TIME = 2
REQUEST_TIMEOUT = 10

start_time = None
tries = 0
successful = 0


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush()


async def try_to_search(session):
    global tries, successful

    tries += 1
    headers = {
        'User-Agent': UserAgent().random
    }
    search_text = 'list comprehension'

    url = 'https://www.google.com/search?client=ubuntu&q={}&oq={}'.format(search_text, search_text)

    try:
        async with session.get(url, headers=headers, timeout=REQUEST_TIMEOUT) as resp:
            resp_text = await resp.text()
            if 'foobar' in resp_text.lower():
                eprint('DEBUG: found foobar keyword')
            
            if 'find.foo' in resp_text.lower():
                eprint('DEBUG: found find.foo keyword')

            matches = re.search(r'(https?://(www.)?google.com/foobar/[^\"]+)', resp_text)
            if matches:
                successful += 1
                print(matches.groups()[0])
                sys.stdout.flush()
                return True
    except (aiohttp.client_exceptions.ServerDisconnectedError,
            aiohttp.client_exceptions.ClientHttpProxyError,
            aiohttp.client_exceptions.ClientProxyConnectionError,
            aiohttp.client_exceptions.ClientResponseError,
            aiohttp.client_exceptions.ClientPayloadError,
            asyncio.TimeoutError,
            aiohttp.client_exceptions.ClientOSError,
            ssl.CertificateError) as ex:
        eprint('Error during request. Proxy: {}. Exception: {}'.format(None, type(ex)))

    return False


async def main():
    global tries, successful

    session_kwargs = {}

    async with aiohttp.ClientSession(**session_kwargs) as session:
        while True:
            tasks = [try_to_search(session) for _ in range(NUMBER_OF_CONCURRENT_TASKS)]

            if tasks:
                await asyncio.gather(*tasks)

            await asyncio.sleep(SLEEP_TIME)


def exit_handler(*_):
    eprint(' tries: {}; successful: {}; took time: {} seconds'.format(tries, successful, time.time() - start_time))
    sys.exit(0)


if __name__ == '__main__':
    start_time = time.time()

    signal.signal(signal.SIGINT, exit_handler)
    parser = argparse.ArgumentParser(
        description='Get your invite to Google\'s programming challenge'
    )
    command_line_args = parser.parse_args()

    asyncio.get_event_loop().run_until_complete(main())
