import minerva.config as config

#from minerva.utils.lazy import LazyLoader

#nltk = LazyLoader('minerva.nlp.wrappers.nltk', 'nltk')

if config.nlp_backend == 'nltk':

    from .wrappers import nltk as tools
else:
    raise Exception(f"Unknown NLP backend '{config.backend}'. Exiting...")

tools_methods = [f for f in dir(tools) if callable(getattr(tools, f)) and not f.startswith("__")]
for method in tools_methods:
    setattr(__import__(__name__), method, getattr(tools, method))

del tools
