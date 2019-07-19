from abc import ABC, abstractmethod
from typing import List

import minerva as mine


class BaseEntity(ABC):

    def __init__(
            self,
            text: str,
            char_index: int = -1,
            language: str = 'en'
    ):
        self.text = text
        self.char_index: int = char_index
        self.end_char_index: int = char_index + len(text) if char_index > 0 else -1
        self.language: str = language

    @abstractmethod
    def __str__(self):
        return self.text


class Token(BaseEntity):

    def __init__(
            self,
            text: str,
            tok_index: int = -1,
            sentence: BaseEntity = None,
            char_index : int = -1,
            language : str = None
    ):
        super().__init__(
            text,
            char_index=char_index,
            language=language
        )
        self.tok_index: int = tok_index
        self.sentence: Sentence = sentence

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return f'Token: {self.text}'


class Sentence(BaseEntity):

    def __init__(
            self,
            text: str,
    ):
        super().__init__(text)
        self.tokens: List[Token] = []

        processed_text = text
        for word in mine.tokenize(text):
            tok_pos = 0 if len(self) == 0 else self.tokens[len(self) - 1].end_char_index
            tok_pos += processed_text.index(word)
            self.tokens.append(Token(
                word,
                tok_index=len(self),
                sentence=self,
                char_index=tok_pos
            ))
            processed_text = text[tok_pos+len(word):]

    def __getitem__(self, idx: int) -> Token:
        return self.tokens[idx]

    def __iter__(self):
        return iter(self.tokens)

    def __len__(self):
        return len(self.tokens)

    def __str__(self):
        return f'Sentence: {self.text}'
