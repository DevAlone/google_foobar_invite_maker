import ssl

import aiosocks
import time
from fake_useragent import UserAgent
from aiosocks.connector import ProxyConnector, ProxyClientRequest

import asyncio
import aiohttp
import argparse
import re
import signal
import sys


NUMBER_OF_CONCURRENT_TASKS_WITHOUT_PROXIES = 1
NUMBER_OF_CONCURRENT_TASKS_WITH_PROXIES = 5000
# in seconds (floating point)
SLEEP_TIME = 3
REQUEST_TIMEOUT = 20
PROXY_API_URL = 'https://proxy.d3d.info/'
# do not touch it! change NUMBER_OF_CONCURRENT_TASKS_WITHOUT_PROXIES and NUMBER_OF_CONCURRENT_TASKS_WITH_PROXIES
NUMBER_OF_CONCURRENT_TASKS = None

start_time = None
tries = 0
successful = 0
# command_line_args = None
use_proxies = False


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush()


async def try_to_search(session, proxy=None):
    global tries, successful

    tries += 1
    headers = {
        'User-Agent': UserAgent().random
    }
    search_text = 'list comprehension'

    url = 'https://www.google.com/search?client=ubuntu&q={}&oq={}'.format(search_text, search_text)

    try:
        async with session.get(url, headers=headers, proxy=proxy, timeout=REQUEST_TIMEOUT) as resp:
            resp_text = await resp.text()

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
            aiosocks.errors.SocksError,
            aiosocks.SocksError,
            asyncio.TimeoutError,
            aiohttp.client_exceptions.ClientOSError,
            ssl.CertificateError) as ex:
        eprint('Error during request. Proxy: {}. Exception: {}'.format(proxy, type(ex)))

    return False


async def main():
    global tries, successful

    session_kwargs = {}

    if use_proxies:
        session_kwargs['connector'] = ProxyConnector(remote_resolve=True)
        session_kwargs['request_class'] = ProxyClientRequest

    async with aiohttp.ClientSession(**session_kwargs) as session:
        while True:
            if use_proxies:
                proxy_request = {
                    'model': 'proxy',
                    'method': 'get',
                    'order_by': 'response_time',
                    'limit': NUMBER_OF_CONCURRENT_TASKS,
                }

                async with session.post(PROXY_API_URL, json=proxy_request) as resp:
                    proxies = (await resp.json())['data']
                    tasks = [try_to_search(session, proxy['address']) for proxy in proxies]
            else:
                tasks = [try_to_search(session) for _ in range(NUMBER_OF_CONCURRENT_TASKS)]

            if tasks:
                await asyncio.wait(tasks)

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
    parser.add_argument('--use-proxies', dest='use_proxies', default='false', help='use proxies (default: false)')
    command_line_args = parser.parse_args()

    use_proxies = command_line_args.use_proxies.lower() == 'true'
    eprint('Started with' + ('out' if not use_proxies else '') + ' proxies')

    if NUMBER_OF_CONCURRENT_TASKS is None:
        NUMBER_OF_CONCURRENT_TASKS = 1000 if use_proxies else 10

    asyncio.get_event_loop().run_until_complete(main())
