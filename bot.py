import logging
import asyncio
import datetime

import aiohttp
from rss_utils import get_first_rss_message, get_random_rss_message
from txt_filter import TxtFilter
from config import BOT_CONFIG


logging.basicConfig(format='%(levelname)s | %(message)s', level='INFO')


class BubaChachaBot(object):
    def __init__(self, token, init_chat_ids=None, init_user_ids=None):
        self.token = token
        self.updates_url = f'{BOT_CONFIG["TELEGRAM_BOT_ROOT_URL"]}' \
                           f'{self.token}/getUpdates'
        self.send_message_url = f'{BOT_CONFIG["TELEGRAM_BOT_ROOT_URL"]}' \
                                f'{self.token}/sendMessage'
        self.logger = logging.getLogger(__name__)
        self.txt_filter = TxtFilter(BOT_CONFIG.get('MSG_FILTER_STRUCT'),
                                    BOT_CONFIG.get('MSG_WORDS_THRESHOLD'))
        self.chat_onetime_ids = []
        self.chat_ids = []
        if init_chat_ids and isinstance(init_chat_ids, list):
            self.chat_ids.extend(init_chat_ids)
        self.chat_filtered_ids = []
        self.msg_filter_user_ids = []
        if init_user_ids and isinstance(init_user_ids, list):
            self.msg_filter_user_ids.extend(init_user_ids)

    async def get_updates(self, update_id=None):
        cnt = 0
        updates_url = self.updates_url
        telegram_retry_count = BOT_CONFIG.get('TELEGRAM_RETRY_COUNT')
        if update_id:
            updates_url += f'?offset={update_id}'
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(updates_url, ssl=False) as resp:
                        resp.raise_for_status()
                        return await resp.json()
            except (aiohttp.ClientResponseError,
                    aiohttp.ClientConnectionError) as exp:
                cnt += 1
                if cnt >= telegram_retry_count:
                    self.logger.error(await resp.text())
                    raise exp
                await asyncio.sleep(5)

    async def send_message(self, message):
        cnt = 0
        telegram_retry_count = BOT_CONFIG.get('TELEGRAM_RETRY_COUNT')
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.send_message_url,
                                            json=message, ssl=False) as resp:
                        resp.raise_for_status()
                        return await resp.json()
            except (aiohttp.ClientResponseError,
                    aiohttp.ClientConnectionError) as exp:
                cnt += 1
                if cnt >= telegram_retry_count:
                    self.logger.error(await resp.text())
                    raise exp
                await asyncio.sleep(5)

    async def update_chat_ids(self):
        update_id = None
        updates = await self.get_updates()
        if 'result' in updates:
            for result_item in updates.get('result'):
                self.logger.info(result_item)
                update_id = result_item.get('update_id')
                if 'message' in result_item:
                    message_item = result_item.get('message')
                    if 'chat' in message_item:
                        chat_id = message_item.get('chat').get('id')
                        chat_msg_raw = message_item.get('text')
                        if chat_msg_raw is None:
                            chat_msg_raw = message_item.get('caption')
                            if chat_msg_raw is None:
                                continue
                        chat_msg = chat_msg_raw.strip().lower()

                        if chat_msg == '/join':
                            if chat_id not in self.chat_ids:
                                self.chat_ids.append(chat_id)
                        elif chat_msg == '/buba':
                            self.chat_onetime_ids.append(chat_id)
                        else:
                            from_id = message_item.get('from').get('id')
                            if from_id in self.msg_filter_user_ids:
                                message_id = message_item.get('message_id')
                                msg_out = self.txt_filter.get_txt_message(
                                    chat_msg, from_id)
                                if msg_out:
                                    self.chat_filtered_ids.append((chat_id,
                                                                   message_id,
                                                                   msg_out))
        if update_id:
            update_id += 1
            self.logger.info(await self.get_updates(update_id))

    async def process_buba_bot(self):
        start_date = datetime.datetime.now()
        telegram_send_msg_timeout = BOT_CONFIG.get(
            'TELEGRAM_SEND_MSG_TIMEOUT')
        telegram_pull_timeout = BOT_CONFIG.get('TELEGRAM_PULL_TIMEOUT')
        telegram_skip_send_msg = BOT_CONFIG.get('TELEGRAM_SKIP_SEND_MSG')
        while True:
            cur_date = datetime.datetime.now()
            await self.update_chat_ids()

            time_delta = (cur_date - start_date).total_seconds()
            if not telegram_skip_send_msg and \
                    time_delta >= telegram_send_msg_timeout:
                text = await get_first_rss_message()
                for chat_id in self.chat_ids:
                    msg_data = {'chat_id': chat_id,
                                'text': text, 'parse_mode': 'HTML'}
                    msg_out = await self.send_message(msg_data)
                    self.logger.info(msg_out)
                    start_date = datetime.datetime.now()

            if self.chat_onetime_ids:
                for chat_onetime_id in self.chat_onetime_ids:
                    cur_text = await get_random_rss_message()
                    msg_data = {'chat_id': chat_onetime_id,
                                'text': cur_text, 'parse_mode': 'HTML'}
                    msg_out = await self.send_message(msg_data)
                    self.logger.info(msg_out)
                self.chat_onetime_ids.clear()

            if self.chat_filtered_ids:
                for chat_item in self.chat_filtered_ids:
                    chat_id, msg_id, msg_txt = chat_item
                    msg_data = {'chat_id': chat_id, 'parse_mode': 'HTML',
                                'reply_to_message_id': msg_id,
                                'text': msg_txt}
                    msg_out = await self.send_message(msg_data)
                    self.logger.info(msg_out)
                self.chat_filtered_ids.clear()

            await asyncio.sleep(telegram_pull_timeout)

    def bot_handler(self):
        asyncio.run(self.process_buba_bot())
