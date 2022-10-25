import asyncio
import random
import xml.etree.ElementTree as etree

import aiohttp
from config import RSS_URL, RSS_RETRY_COUNT, \
    MSG_HEADER, MSG_ADJECTIVES, MSG_END


async def fetch_rss():
    try_count = 0
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(RSS_URL, ssl=False) as resp:
                    resp.raise_for_status()
                    return await resp.text()
        except (aiohttp.ClientResponseError,
                aiohttp.ClientConnectionError) as exp:
            try_count += 1
            if try_count >= RSS_RETRY_COUNT:
                raise exp
            await asyncio.sleep(3)


async def get_first_rss_title():
    rss_txt = await fetch_rss()
    rss_xml = etree.fromstring(rss_txt)
    rss_title = rss_xml.find('channel/item/title')
    if rss_title is not None:
        return rss_title.text.strip()


async def get_random_rss_title():
    rss_txt = await fetch_rss()
    rss_xml = etree.fromstring(rss_txt)
    rss_items = rss_xml.findall('channel/item')
    if rss_items is not None:
        rss_item = random.choice(rss_items)
        rss_title = rss_item.find('title')
        if rss_title is not None:
            return rss_title.text.strip()


async def get_random_message():
    rss_title = await get_random_rss_title()
    adjective = random.choice(MSG_ADJECTIVES)
    txt = f'{MSG_HEADER}\n{rss_title}'\
          f'\n\n А {adjective} {MSG_END}'
    return txt


async def get_first_message():
    rss_title = await get_first_rss_title()
    adjective = random.choice(MSG_ADJECTIVES)
    txt = f'{MSG_HEADER}\n{rss_title}'\
          f'\n\n А {adjective} {MSG_END}'
    return txt
