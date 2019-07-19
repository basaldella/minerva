import nltk


def tokenize(txt, language='english'):
    return nltk.word_tokenize(txt, language)


def pos_tag(txt, language='english'):

    if isinstance(txt, str):
        return nltk.pos_tag(nltk.word_tokenize(txt, language=language), lang=language)
    else:
        return nltk.pos_tag(txt, lang=language)
