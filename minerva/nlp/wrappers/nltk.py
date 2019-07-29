import nltk  # type: ignore
from typing import List, Tuple

TOKENIZER = None


def sent_tokenize(txt: str, language: str = "english") -> List[str]:

    return nltk.sent_tokenize(txt, language)  # type: ignore


def word_tokenize(txt: str, language: str = "english") -> List[str]:

    global TOKENIZER

    if not TOKENIZER:
        TOKENIZER = nltk.tokenize.WordPunctTokenizer()

    return TOKENIZER.tokenize(txt)  # type: ignore


def pos_tag(txt: str, language: str = "english") -> List[Tuple[str, str]]:

    ret: List[Tuple[str, str]]
    if isinstance(txt, str):
        ret = nltk.pos_tag(nltk.word_tokenize(txt, language=language), lang=language)
    else:
        ret = nltk.pos_tag(txt, lang=language)

    return ret
