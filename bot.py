import logging
import asyncio
import datetime

import aiohttp
from rss_utils import get_first_rss_message, get_random_rss_message
from txt_filter import TxtFilter
from photo_filter import PhotoFilter
from config import BOT_CONFIG


logging.basicConfig(format='%(levelname)s | %(message)s', level='INFO')


class BubaChachaBot(object):
    def __init__(self, token, init_chat_ids=None,
                 init_user_ids=None, init_photo_user_ids=None,
                 init_photo_chat_ids=None):
        self.logger = logging.getLogger(__name__)
        self.token = token
        self.updates_url = f'{BOT_CONFIG["TELEGRAM_BOT_ROOT_URL"]}' \
                           f'{self.token}/getUpdates'
        self.send_message_url = f'{BOT_CONFIG["TELEGRAM_BOT_ROOT_URL"]}' \
                                f'{self.token}/sendMessage'
        self.send_video_url = f'{BOT_CONFIG["TELEGRAM_BOT_ROOT_URL"]}'\
                              f'{self.token}/sendVideo'
        self.get_file_url = f'{BOT_CONFIG["TELEGRAM_BOT_ROOT_URL"]}'\
                            f'{self.token}/getFile'
        self.forward_message_url = f'{BOT_CONFIG["TELEGRAM_BOT_ROOT_URL"]}' \
                                   f'{self.token}/forwardMessage'
        self.txt_filter = TxtFilter(BOT_CONFIG.get('MSG_FILTER_STRUCT'),
                                    BOT_CONFIG.get('MSG_WORDS_THRESHOLD'))
        self.photo_filter = PhotoFilter(BOT_CONFIG.get('PHOTO_YOLO_MODEL'),
                                        BOT_CONFIG.get('PHOTO_YOLO_THRESHOLD'),
                                        BOT_CONFIG.get('PHOTO_YOLO_CLASSES'))
        self.chat_onetime_ids = []
        self.chat_ids = []
        if init_chat_ids and isinstance(init_chat_ids, list):
            self.chat_ids.extend(init_chat_ids)
        self.msg_filter_user_ids = []
        if init_user_ids and isinstance(init_user_ids, list):
            self.msg_filter_user_ids.extend(init_user_ids)
        self.photo_user_ids = []
        if init_photo_user_ids and isinstance(init_photo_user_ids, list):
            self.photo_user_ids.extend(init_photo_user_ids)
        self.photo_chat_ids = []
        if init_photo_chat_ids and isinstance(init_photo_chat_ids, list):
            self.photo_chat_ids.extend(init_photo_chat_ids)
        self.chat_filtered_tasks = []
        self.photo_filtered_tasks = []

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
                        json_out = await resp.json()
                        resp.raise_for_status()
                        return json_out
            except (aiohttp.ClientResponseError,
                    aiohttp.ClientConnectionError) as exp:
                cnt += 1
                if cnt >= telegram_retry_count:
                    self.logger.error(json_out)
                    raise exp
                await asyncio.sleep(5)

    async def send_message(self, message):
        cnt = 0
        telegram_retry_count = BOT_CONFIG.get('TELEGRAM_RETRY_COUNT')
        message_url = self.send_message_url
        if 'video' in message:
            message_url = self.send_video_url
        elif 'from_chat_id' in message:
            message_url = self.forward_message_url
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(message_url,
                                            json=message, ssl=False) as resp:
                        json_out = await resp.json()
                        resp.raise_for_status()
                        return json_out
            except (aiohttp.ClientResponseError,
                    aiohttp.ClientConnectionError) as exp:
                cnt += 1
                if cnt >= telegram_retry_count:
                    self.logger.error(exp)
                    self.logger.error(json_out)
                    return
                await asyncio.sleep(5)

    async def download_file(self, file_id):
        cnt = 0
        telegram_retry_count = BOT_CONFIG.get('TELEGRAM_RETRY_COUNT')
        get_file_url = self.get_file_url + f'?file_id={file_id}'
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    # self.logger.info(get_file_url)
                    async with session.get(get_file_url, ssl=False) as resp:
                        json_out = await resp.json()
                        resp.raise_for_status()
                        file_path = json_out.get('result').get('file_path')
                    file_url = f'{BOT_CONFIG["TELEGRAM_BOT_FILE_URL"]}' \
                               f'{self.token}/{file_path}'
                    # self.logger.info(file_url)
                    async with session.get(file_url, ssl=False) as resp:
                        resp.raise_for_status()
                        file_data = await resp.read()
                        return file_data
            except (aiohttp.ClientResponseError,
                    aiohttp.ClientConnectionError) as exp:
                cnt += 1
                if cnt >= telegram_retry_count:
                    self.logger.error(json_out)
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
                        from_id = message_item.get('from').get('id')
                        message_id = message_item.get('message_id')
                        if from_id in self.photo_user_ids:
                            photo = message_item.get('photo')
                            is_forward = message_item.get('forward_from_chat')
                            if photo and not is_forward:
                                photo_item = photo[-1]
                                photo_out_item = {'from_chat_id': chat_id,
                                                  'message_id': message_id,
                                                  'photo': photo_item}
                                self.photo_filtered_tasks.append(
                                    photo_out_item)

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
                            if from_id in self.msg_filter_user_ids:
                                msg_raw = self.txt_filter.get_txt_message(
                                    chat_msg, from_id)
                                if msg_raw:
                                    msg_out_item = {'chat_id': chat_id,
                                                    'message_id': message_id,
                                                    'msg_out': msg_raw[0],
                                                    'msg_type': msg_raw[1]}
                                    self.chat_filtered_tasks.append(
                                        msg_out_item)
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

            if self.chat_filtered_tasks:
                for chat_item in self.chat_filtered_tasks:
                    if chat_item.get('msg_type') == 'video':
                        msg_data = {'chat_id': chat_item.get('chat_id'),
                                    'reply_to_message_id':
                                        chat_item.get('message_id'),
                                    'video': chat_item.get('msg_out')}
                    else:
                        msg_data = {'chat_id': chat_item.get('chat_id'),
                                    'reply_to_message_id':
                                        chat_item.get('message_id'),
                                    'parse_mode': 'HTML',
                                    'text': chat_item.get('msg_out')}
                    msg_out = await self.send_message(msg_data)
                    self.logger.info(msg_out)
                self.chat_filtered_tasks.clear()

            if self.photo_filtered_tasks:
                for photo_item in self.photo_filtered_tasks:
                    from_chat_id = photo_item.get('from_chat_id')
                    message_id = photo_item.get('message_id')
                    photo_file_id = photo_item.get('photo').get('file_id')
                    photo_content = await self.download_file(photo_file_id)
                    res = await self.photo_filter.is_photo_valid_async(
                        photo_content)
                    if res:
                        for photo_chat_id in self.photo_chat_ids:
                            msg_data = {'disable_notification': False,
                                        'chat_id': photo_chat_id,
                                        'from_chat_id': from_chat_id,
                                        'message_id': message_id}
                            msg_out = await self.send_message(msg_data)
                            self.logger.info(msg_out)
                self.photo_filtered_tasks.clear()

            await asyncio.sleep(telegram_pull_timeout)

    def bot_handler(self):
        asyncio.run(self.process_buba_bot())
