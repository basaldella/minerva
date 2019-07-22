import minerva.config as config

# from minerva.utils.lazy import LazyLoader

# nltk = LazyLoader('minerva.nlp.wrappers.nltk', 'nltk')

if config.nlp_backend == "nltk":

    from minerva.nlp.wrappers.nltk import *
else:
    raise Exception(f"Unknown NLP backend '{config.nlp_backend}'. Exiting...")
