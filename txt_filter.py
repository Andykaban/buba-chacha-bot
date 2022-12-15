import logging
import random
import string

import Levenshtein

logging.basicConfig(format='%(levelname)s | %(message)s', level='INFO')

ALPHABET = {'а': ['а', 'a', '@'],
            'б': ['б', '6', 'b'],
            'в': ['в', 'b', 'v'],
            'г': ['г', 'r', 'g'],
            'д': ['д', 'd'],
            'е': ['е', 'e'],
            'ё': ['ё', 'e'],
            'ж': ['ж', 'zh', '*'],
            'з': ['з', '3', 'z'],
            'и': ['и', 'u', 'i'],
            'й': ['й', 'u', 'i'],
            'к': ['к', 'k', 'i{', '|{'],
            'л': ['л', 'l', 'ji'],
            'м': ['м', 'm'],
            'н': ['н', 'h', 'n'],
            'о': ['о', 'o', '0'],
            'п': ['п', 'n', 'p'],
            'р': ['р', 'r', 'p'],
            'с': ['с', 'c', 's'],
            'т': ['т', 'm', 't'],
            'у': ['у', 'y', 'u'],
            'ф': ['ф', 'f'],
            'х': ['х', 'x', 'h', '}{'],
            'ц': ['ц', 'c', 'u,'],
            'ч': ['ч', 'ch'],
            'ш': ['ш', 'sh'],
            'щ': ['щ', 'sch'],
            'ь': ['ь', 'b'],
            'ы': ['ы', 'bi'],
            'ъ': ['ъ'],
            'э': ['э', 'e'],
            'ю': ['ю', 'io'],
            'я': ['я', 'ya']}


class TxtFilter(object):

    def __init__(self, search_data, word_threshold):
        self.search_data = search_data
        self.word_threshold = word_threshold
        self.logger = logging.getLogger()

    def get_txt_message_simple(self, search_item, txt, user_id=None):
        norm_txt = ''.join([i for i in txt.strip().lower()
                            if i not in string.punctuation])
        norm_txt = norm_txt.replace('\n', '').replace('\r',
                                                      '').replace('\\', '')
        norm_txt = norm_txt.replace('zh', 'ж').replace(
            'i{', 'к').replace('|{', 'к').replace(
            'ji', 'л').replace('}{', 'х').replace(
            'ch', 'ч').replace('sch', 'щ').replace(
            'bi', 'ы').replace('io', 'ю').replace('ya', 'я')
        for key, val in ALPHABET.items():
            for letter in val:
                for symbol_txt in norm_txt:
                    if letter == symbol_txt:
                        norm_txt = norm_txt.replace(symbol_txt, key)
        # self.logger.info(norm_txt)

        search_words = search_item.get('filter_words')
        cur_threshold = self.word_threshold
        if 'filter_threshold' in search_item:
            cur_threshold = float(search_item.get('filter_threshold'))
        for word in search_words:
            for message_word in norm_txt.split():
                distance = Levenshtein.distance(message_word, word)
                if distance <= cur_threshold * len(word):
                    self.logger.info(f'Found {word} '
                                     f'like by {message_word}')
                    answers = search_item.get('common_replies')
                    if user_id:
                        user_answers_key = f'{user_id}_replies'
                        user_answers = search_item.get(user_answers_key)
                        if user_answers:
                            answers.extend(user_answers)
                    random.shuffle(answers)
                    return random.choice(answers)

    def get_txt_message_orig(self, search_item, txt, user_id=None):
        # Text normalization
        norm_txt = txt.strip().lower().replace(' ', '')
        for key, val in ALPHABET.items():
            for letter in val:
                for symbol_txt in norm_txt:
                    if letter == symbol_txt:
                        norm_txt = norm_txt.replace(symbol_txt, key)
        # self.logger.info(norm_txt)

        search_words = search_item.get('filter_words')
        cur_threshold = self.word_threshold
        if 'filter_threshold' in search_item:
            cur_threshold = float(search_item.get('filter_threshold'))
        for word in search_words:
            for part in range(len(norm_txt)):
                txt_fragment = norm_txt[part:part + len(word)]
                distance = Levenshtein.distance(txt_fragment, word)
                if distance <= cur_threshold * len(word):
                    self.logger.info(f'Found {word} '
                                     f'like by {txt_fragment}')
                    answers = search_item.get('common_replies')
                    if user_id:
                        user_answers_key = f'{user_id}_replies'
                        user_answers = search_item.get(user_answers_key)
                        if user_answers:
                            answers.extend(user_answers)
                    random.shuffle(answers)
                    return random.choice(answers)

    def get_txt_message(self, txt, user_id=None):
        for search_item in self.search_data:
            search_mode = search_item.get('filter_mode')
            if search_mode == 'simple':
                txt_message = self.get_txt_message_simple(search_item,
                                                          txt, user_id)
            else:
                txt_message = self.get_txt_message_orig(search_item,
                                                        txt, user_id)
            if txt_message:
                return txt_message
