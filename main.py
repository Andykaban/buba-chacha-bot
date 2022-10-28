import argparse

from bot import BubaChachaBot
from config import TELEGRAM_DEFAULT_CHAT_IDS, MSG_FILTER_USER_IDS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bot-token', dest='bot_token', required=True)
    parser.add_argument('--chat-ids', dest='chat_ids', default='')
    parser.add_argument('--user-ids', dest='user_ids', default='')
    args = parser.parse_args()

    chat_ids = [int(i) for i in args.chat_ids.split(',')
                if i.lstrip('-').isdigit()]
    if TELEGRAM_DEFAULT_CHAT_IDS:
        chat_ids.extend(TELEGRAM_DEFAULT_CHAT_IDS)
    user_ids = [int(i) for i in args.user_ids.split(',') if i.isdigit()]
    if MSG_FILTER_USER_IDS:
        user_ids.extend(MSG_FILTER_USER_IDS)
    buba_bot = BubaChachaBot(args.bot_token, chat_ids, user_ids)
    buba_bot.bot_handler()


if __name__ == '__main__':
    main()
