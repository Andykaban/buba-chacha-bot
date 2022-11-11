import asyncio
import random
import xml.etree.ElementTree as etree

import aiohttp
from config import BOT_CONFIG


async def fetch_rss():
    try_count = 0
    rss_url = BOT_CONFIG.get('RSS_URL')
    rss_retry_count = BOT_CONFIG.get('RSS_RETRY_COUNT')
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(rss_url, ssl=False) as resp:
                    resp.raise_for_status()
                    return await resp.text()
        except (aiohttp.ClientResponseError,
                aiohttp.ClientConnectionError) as exp:
            try_count += 1
            if try_count >= rss_retry_count:
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


async def get_random_rss_message():
    rss_title = await get_random_rss_title()
    msg_header = BOT_CONFIG.get('MSG_HEADER')
    adjective = random.choice(BOT_CONFIG.get('MSG_ADJECTIVES'))
    msg_pretext = BOT_CONFIG.get('MSG_PRETEXT')
    msg_end = BOT_CONFIG.get('MSG_END')
    txt = f'{msg_header}\n{rss_title}'\
          f'\n\n{msg_pretext} {adjective} {msg_end}'
    return txt


async def get_first_rss_message():
    rss_title = await get_first_rss_title()
    msg_header = BOT_CONFIG.get('MSG_HEADER')
    adjective = random.choice(BOT_CONFIG.get('MSG_ADJECTIVES'))
    msg_pretext = BOT_CONFIG.get('MSG_PRETEXT')
    msg_end = BOT_CONFIG.get('MSG_END')
    txt = f'{msg_header}\n{rss_title}' \
          f'\n\n{msg_pretext} {adjective} {msg_end}'
    return txt
