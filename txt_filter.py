import logging
import random

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

    def get_txt_message(self, txt, user_id=None):
        # Text normalization
        norm_txt = txt.strip().lower().replace(' ', '')
        for key, val in ALPHABET.items():
            for letter in val:
                for symbol_txt in norm_txt:
                    if letter == symbol_txt:
                        norm_txt = norm_txt.replace(symbol_txt, key)
        # self.logger.info(norm_txt)

        for search_item in self.search_data:
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
                        return random.choice(answers)
