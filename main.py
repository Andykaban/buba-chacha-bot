import argparse

import config
from bot import BubaChachaBot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bot-token', dest='bot_token', required=True)
    parser.add_argument('--bot-config',
                        dest='bot_config', default='bot-config.yaml')
    parser.add_argument('--chat-ids', dest='chat_ids', default='')
    parser.add_argument('--user-ids', dest='user_ids', default='')
    parser.add_argument('--photo-user-ids', dest='photo_user_ids', default='')
    parser.add_argument('--photo-redirect-ids',
                        dest='photo_redirect_ids', default='')
    parser.add_argument('--photo-redirect-chat-ids',
                        dest='photo_redirect_chat_ids', default='')
    args = parser.parse_args()

    config.load_config(args.bot_config)
    chat_ids = [int(i) for i in args.chat_ids.split(',')
                if i.lstrip('-').isdigit()]
    if config.BOT_CONFIG.get('TELEGRAM_DEFAULT_CHAT_IDS'):
        chat_ids.extend(config.BOT_CONFIG.get('TELEGRAM_DEFAULT_CHAT_IDS'))
    user_ids = [int(i) for i in args.user_ids.split(',') if i.isdigit()]
    if config.BOT_CONFIG.get('MSG_FILTER_USER_IDS'):
        user_ids.extend(config.BOT_CONFIG.get('MSG_FILTER_USER_IDS'))
    photo_user_ids = [int(i) for i in args.photo_user_ids.split(',')
                      if i.isdigit()]
    if config.BOT_CONFIG.get('PHOTO_YOLO_USER_IDS'):
        photo_user_ids.extend(config.BOT_CONFIG.get('PHOTO_YOLO_USER_IDS'))
    photo_chat_ids = [int(i) for i in args.photo_redirect_chat_ids.split(',')
                      if i.lstrip('-').isdigit()]
    if config.BOT_CONFIG.get('PHOTO_YOLO_CHAT_IDS'):
        photo_chat_ids.extend(config.BOT_CONFIG.get('PHOTO_YOLO_CHAT_IDS'))

    buba_bot = BubaChachaBot(args.bot_token, chat_ids, user_ids,
                             photo_user_ids, photo_chat_ids)
    buba_bot.bot_handler()


if __name__ == '__main__':
    main()
