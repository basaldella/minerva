from abc import ABC, abstractmethod
from typing import Any, Dict, List, Iterable, Optional, Union

import minerva as mine


class Annotation(ABC):
    def __init__(
        self, value: str, score: Optional[float] = None, **kwargs: Dict[str, Any]
    ):
        self.value: str = value
        self.__annos = {}
        for key, value in kwargs:
            self[key] == value

        if score:
            self["score"] == score

    def __setitem__(self, key: str, value: Any) -> None:

        if key == "value":
            raise ValueError(
                "'value' is a forbidden annotation. Use the class attribute instead."
            )
        else:
            self.__annos[key] = value

    def __getitem__(self, item: str) -> Any:
        if item == "value":
            return self.value
        else:
            return self.__annos[item]


class TokenSpan(Annotation):
    def __init__(
        self,
        value: str,
        start: "Token",
        end: "Token",
        score: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(value, score)
        super()["start"] = start.index
        super()["end"] = end.index
        for key, value in kwargs:
            super()[key] == value

    @property
    def end(self) -> "Token":
        return self["end"]

    @property
    def start(self) -> "Token":
        return self["start"]

    @property
    def text(self) -> str:
        return self.start.parent[self.start.char_index, self.start.end_char_index]


class BaseEntity(ABC):
    def __init__(self, text: str, language: str = "en"):
        self.text: str = text
        self.language: str = language

    @abstractmethod
    def __str__(self) -> str:
        return self.text


class BaseTextualEntity(BaseEntity):
    def __init__(
        self, text: str, index: int = -1, char_index: int = -1, language: str = "en"
    ):
        super().__init__(text, language=language)
        self.index: int = index
        self.char_index: int = char_index
        self.end_char_index: int = char_index + len(text) if char_index >= 0 else -1
        self.labels: Dict[str, Annotation] = {}

    @abstractmethod
    def __str__(self) -> str:
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

    def __setitem__(self, key: str, value: Any) -> None:
        self.labels[key] = value

    def __getitem__(self, item: str) -> Any:
        return self.labels[item]

    def __iter__(self) -> Iterable:
        return iter(self.labels)

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
        self.annotations: Dict[str, Annotation] = {}

        # generate tokens
        processed_text = text
        for word in mine.word_tokenize(text):
            tok_pos = 0 if len(self) == 0 else self.tokens[len(self) - 1].end_char_index
            tok_pos += processed_text.index(word)
            self.tokens.append(
                Token(word, index=len(self), parent=self, char_index=tok_pos)
            )
            processed_text = text[tok_pos + len(word) :]

    def add_annotation(
        self,
        key: str,
        value: str,
        begin: int = None,
        end: int = None,
        score: int = None,
        **kwargs,
    ) -> None:
        if begin and end:
            ann = TokenSpan(value, self[begin], self[end], score, **kwargs)
            for token in self[begin:end]:
                token[key] = ann

        else:
            self.annotations[key] = Annotation(value, score, **kwargs)

    def get_annotation(self, key: str) -> Union[Annotation, List[Annotation]]:

        if key in self.annotations:
            return self.annotations[key]

        anns: List[Annotation] = []

        i = 0
        while i < len(self):

            token = self[i]
            if key in token:
                if isinstance(token[key], TokenSpan):
                    i = token[key].end.index

                anns.append(token[key])
            i += 1

        if len(anns) > 0:
            return anns
        else:
            raise KeyError(f"{key} is not an annotation for this sentence.")

    def token_at_char(self, index: int) -> Optional[Token]:
        """
        Return the token at position `index`. Performed using binary search,
         hence runtime is $O(log(n))$. If the there is no token at the given
          index (e.g. the index points to a whitespace), returns None.

        :param index: a character position within the string
        :return: the token at position `index`, or None if `index`
        points to a non-token character.
        """

        if index < 0 or index > len(self.text):
            raise IndexError(
                f"index {index} is too small/big for the sentence '{self.text}'"
            )

        token: Optional[Token] = None

        left = 0
        right = len(self) - 1

        while left <= right:
            middle = (left + right) // 2

            if self[middle].char_index <= index <= self[middle].end_char_index - 1:
                token = self[middle]
                break
            elif index < self[middle].char_index:
                right = middle - 1
            else:
                left = middle + 1

        return token

    def __getitem__(self, idx: int) -> Token:
        return self.tokens[idx]

    def __iter__(self) -> Iterable:
        return iter(self.tokens)

    def __len__(self) -> int:
        return len(self.tokens)

    def __str__(self) -> str:
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

    def __iter__(self) -> Iterable:
        return iter(self.sentences)

    def __len__(self) -> int:
        return len(self.sentences)

    def __str__(self) -> str:
        return f"Document: {self.text}"


class Corpus:
    def __init__(self, _id: str = None, items: List[BaseEntity] = None):
        self.id: Optional[str] = _id
        self.items: List[BaseEntity]

        if items:
            self.items = items
        else:
            self.items = []

    def add(self, item: BaseEntity) -> None:
        self.items.append(item)

    def __add__(self, other) -> "Corpus":
        new_id = self.id + " + " + other.id if self.id and other.id else ""
        return Corpus(new_id, self.items + other.items)

    def __getitem__(self, idx: int) -> BaseEntity:
        return self.items[idx]

    def __iter__(self) -> Iterable:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __str__(self) -> str:
        return f"Corpus: {self.id} ({len(self)} items)"
