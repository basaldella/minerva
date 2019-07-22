from abc import ABC, abstractmethod
from typing import List, Optional, Union

import minerva as mine


class BaseEntity(ABC):
    def __init__(self, text: str, language: str = "en"):
        self.text: str = text
        self.language: str = language

    @abstractmethod
    def __str__(self):
        return self.text


class BaseTextualEntity(BaseEntity):
    def __init__(
        self, text: str, index: int = -1, char_index: int = -1, language: str = "en"
    ):
        super().__init__(text, language=language)
        self.index: int = index
        self.char_index: int = char_index
        self.end_char_index: int = char_index + len(text) if char_index > 0 else -1

    @abstractmethod
    def __str__(self):
        return self.text


class Token(BaseTextualEntity):
    def __init__(
        self,
        text: str,
        index: int = -1,
        parent: BaseTextualEntity = None,
        char_index: int = -1,
        language: str = "en",
    ):
        super().__init__(text, index=index, char_index=char_index, language=language)
        self.parent: Optional[BaseTextualEntity] = parent

    def __len__(self) -> int:
        return len(self.text)

    def __str__(self) -> str:
        if self.parent and self.parent.index >= 0:
            index = (
                f"[{self.parent.index}][{str(self.index)}]" if self.index >= 0 else ""
            )
        else:
            index = f"[{str(self.index)}]" if self.index >= 0 else ""
        return f"Token {index}: {self.text}"


class Sentence(BaseTextualEntity):
    def __init__(self, text: str, index: int = -1):
        super().__init__(text, index=index)
        self.tokens: List[Token] = []

        # generate tokens
        processed_text = text
        for word in mine.word_tokenize(text):
            tok_pos = 0 if len(self) == 0 else self.tokens[len(self) - 1].end_char_index
            tok_pos += processed_text.index(word)
            self.tokens.append(
                Token(word, index=len(self), parent=self, char_index=tok_pos)
            )
            processed_text = text[tok_pos + len(word) :]

    def __getitem__(self, idx: int) -> Token:
        return self.tokens[idx]

    def __iter__(self):
        return iter(self.tokens)

    def __len__(self):
        return len(self.tokens)

    def __str__(self):
        index = f"[{str(self.index)}]" if self.index >= 0 else ""
        return f"Sentence {index}: {self.text}"


class Document(BaseEntity):
    def __init__(self, text: str, _id: Optional[str] = None, language: str = "en"):

        if isinstance(text, str):
            super().__init__(text=text, language=language)
        else:
            super().__init__(text="\n".join(text), language=language)

        sentences_txt = mine.sent_tokenize(text) if isinstance(text, str) else text

        self.sentences: List[Sentence] = [
            Sentence(sentences_txt[i], index=i) for i in range(len(sentences_txt))
        ]
        self.id: Optional[str] = _id

    def __getitem__(self, idx: int) -> Sentence:
        return self.sentences[idx]

    def __iter__(self):
        return iter(self.sentences)

    def __len__(self):
        return len(self.sentences)

    def __str__(self):
        return f"Document: {self.text}"


class Corpus:
    def __init__(self, _id: str = None, items: List[BaseEntity] = None):
        self.id: Optional[str] = _id
        self.items: List[BaseEntity]

        if items:
            self.items = items
        else:
            self.items = []

    def add(self, item: BaseEntity):
        self.items.append(item)

    def __add__(self, other):
        new_id = self.id + " + " + other.id if self.id and other.id else ""
        return Corpus(new_id, self.items + other.items)

    def __getitem__(self, idx: int) -> BaseEntity:
        return self.items[idx]

    def __iter__(self):
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __str__(self) -> str:
        return f"Corpus: {self.id} ({len(self)} items)"
