import logging

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

    def __init__(self, search_words, word_threshold):
        self.search_words = search_words
        self.word_threshold = word_threshold
        self.logger = logging.getLogger()

    def is_contain(self, txt):
        # Text normalization
        norm_txt = txt.strip().lower().replace(' ', '')
        for key, val in ALPHABET.items():
            for letter in val:
                for symbol_txt in norm_txt:
                    if letter == symbol_txt:
                        norm_txt = norm_txt.replace(symbol_txt, key)
        # self.logger.info(norm_txt)

        # Text search
        for word in self.search_words:
            for part in range(len(norm_txt)):
                txt_fragment = norm_txt[part:part+len(word)]
                distance = Levenshtein.distance(txt_fragment, word)
                if distance <= self.word_threshold * len(word):
                    self.logger.info(f'Found {word} like by {txt_fragment}')
                    return True
