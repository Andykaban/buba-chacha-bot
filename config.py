# TELEGRAM_SETTINGS
TELEGRAM_BOT_ROOT_URL = 'https://api.telegram.org/bot'
TELEGRAM_RETRY_COUNT = 50
TELEGRAM_PULL_TIMEOUT = 10
TELEGRAM_SEND_MSG_TIMEOUT = 7200
TELEGRAM_DEFAULT_CHAT_IDS = []

# RSS SETTINGS
RSS_URL = 'https://lenta.ru/rss'
RSS_RETRY_COUNT = 50

# Message settings
MSG_HEADER = '<b>Новости с пометкой ⚡</b>'
MSG_ADJECTIVES = ['вонючий', 'мерзкий', 'говнистый', 'подлый',
                  'паскудный', 'поганый', 'гнусный', '',
                  'жалкий', 'убогий', 'никчёмный']
MSG_END = 'бубочка все еще не завел канал про чачу...'

# Message filer settings
MSG_FILTER_WORDS = ['вятич']
MSG_WORDS_THRESHOLD = 0.25
MSG_FILTER_USER_IDS = []
MSG_FILTER_REPLIES = ['Опять вятич петух закукарекал! Заместо Авроры',
                      'Кто любит пить вятич тот любит сосать хуй'
                      'Вятич, вятич - в сортах говна не разбираюсь',
                      'Вятич, КУД-КУ-ДАХ!',
                      'Опять вонючка рот раскрыл',
                      'Юринов ИльAss - хуесос и пидарас',
                      'Опять про ебаную мочу']
