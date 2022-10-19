import argparse

from bot import BubaChachaBot
from config import TELEGRAM_DEFAULT_CHAT_IDS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bot-token', dest='bot_token', required=True)
    args = parser.parse_args()

    buba_bot = BubaChachaBot(args.bot_token, TELEGRAM_DEFAULT_CHAT_IDS)
    buba_bot.bot_handler()


if __name__ == '__main__':
    main()
