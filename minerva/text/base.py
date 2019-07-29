from abc import ABC, abstractmethod
from typing import Any, Dict, List, Iterable, Optional, overload, Union

import minerva as mine


class Annotation(ABC):
    def __init__(
        self, value: str, score: Optional[float] = None, **kwargs: Dict[str, Any]
    ):
        """
        A basic annotation. It must hold at least a value (e.g. a part-of-speech tag). Optionally, it can
        have a confidence score. Any other keyword parameter is added to the annotation internal dictionary.

        For example, you can call `Annotation('Noun')`, or `Annotation('ontology-object', score=0.75,
        url='http://ontology.org/object')`

        :param value: the value of the annotation
        :param score: an optional confidence score
        :param kwargs: additional information to store into the annotation
        """
        self.value: str = value
        self.__annos: Dict[str, Any] = {}
        for key, value in kwargs:
            self[key] = value

        if score:
            self["score"] = score

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Sets/updates an annotation field with a new value.

        :param key: the field to set/update.
        :param value: the new value of the field.
        """

        if key == "value":
            raise ValueError(
                "'value' is a forbidden annotation. Use the class attribute instead."
            )
        else:
            self.__annos[key] = value

    def __getitem__(self, item: str) -> Any:
        """
        Get a field value from the annotation.

        :param item: the key of the field to retrieve.
        :return: the annotation value.
        """
        if item == "value":
            return self.value
        else:
            if item in self.__annos:
                return self.__annos[item]
            else:
                raise KeyError(f"{item} is not a valid annotation field.")


class TokenSpan(Annotation):
    """
    An annotation over more than one token.
    """

    def __init__(
        self,
        value: str,
        start_token: "Token",
        end_token: "Token" = None,
        score: Optional[float] = None,
        **kwargs,
    ):
        """
        Instantiates the multi-token annotation. If the annotation spans only one token, it can
        be called omitting `end_token`. Additional keyword arguments will be stored in the annotation
        dictionary.

        :param value: the value of the annotation.
        :param start_token: the first token of the span.
        :param end_token: the last token on the span.
        :param score: the score of the annotation.
        :param kwargs: additional keyword arguments, to be stored within the annotation.
        """

        if not end_token:
            end_token = start_token

        super().__init__(value, score)
        self["start_token"] = start_token
        self["end_token"] = end_token
        for key, value in kwargs:
            self[key] = value

    @property
    def start_token(self) -> "Token":
        """
        Retrieves the first token of the annotation.

        :return: the first token of the annotation
        """
        t: "Token" = self["start_token"]
        return t

    @property
    def end_token(self) -> "Token":
        """
        Retrieves the last token of the annotation.

        :return: the last token of the annotation.
        """
        t: "Token" = self["end_token"]
        return t

    @property
    def start_index(self) -> int:
        """
        Returns the index of the first token within its parent (e.g. a Sentence).

        :return: a the index of the first token.
        """
        return self.start_token.index

    @property
    def end_index(self) -> int:
        """
        Returns the index of the last token within its parent (e.g. a Sentence).

        :return: a the index of the last token.
        """
        return self.end_token.index

    @property
    def text(self) -> str:
        """
        Returns the text span covered by the annotation.

        :return: the text span covered by the annotations.
        """
        if self.start_token.parent:
            return self.start_token.parent.text[
                self.start_token.char_index : self.end_token.end_char_index
            ]

        raise ValueError(
            "This TokenSpan was probably not created from a sentence. You should always use \
            `Sentence.add_annotation` for creating TokenSpans"
        )


class BaseEntity(ABC):
    """
    A basic entity.
    """

    def __init__(self, text: str, language: str = "en"):
        """
        Initializes the entity.

        :param text: the text of the entity.
        :param language: the language of the entity.
        """
        self.text: str = text
        self.language: str = language

    def __str__(self) -> str:
        """
        The text of the entity, as passed to the constructor.

        :return: the text of the entity
        """
        return self.text


class BaseTextualEntity(BaseEntity):
    """
    A basic textual entity, potentially part of other, bigger textual entities. For example, it could represent
    a word, which may be part of a sentence, which may be part of a document; of it could represent a tweet, and so on.

    As part of a bigger whole, it may have an index within its parent (e.g. it could be the 3rd sentence) and a
    character index (e.g. it could be the word starting at character 45).
    """

    def __init__(
        self,
        text: str,
        index: int = -1,
        char_index: int = -1,
        language: str = "en",
        parent: BaseEntity = None,
    ):
        """
        Creates the textual entity.

        :param text: the text of the entity, as it appears in the original source.
        :param index: the index of the entity (e.g. the third token of a sentence).
        :param char_index: the character index of the entity (e.g. a token may appear at character 45).
        :param language: the language of the entity.
        :param parent: the parent entity.
        """
        super().__init__(text, language=language)
        self.index: int = index
        self.char_index: int = char_index
        self.end_char_index: int = char_index + len(text) if char_index >= 0 else -1
        self.labels: Dict[str, Annotation] = {}
        self.parent: Optional[BaseEntity] = parent


class Token(BaseTextualEntity):
    def __init__(
        self,
        text: str,
        index: int = -1,
        parent: BaseTextualEntity = None,
        char_index: int = -1,
        language: str = "en",
    ):
        super().__init__(
            text, index=index, char_index=char_index, language=language, parent=parent
        )

    def __contains__(self, item):
        return item in self.labels.keys()

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
    def __init__(self, text: str, index: int = -1, parent: BaseEntity = None):
        super().__init__(text, index=index, parent=parent)
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
        score: float = None,
        **kwargs,
    ) -> None:
        if begin and end:
            ann = TokenSpan(value, self[begin], self[end - 1], score, **kwargs)
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
                    i = token[key].end_index

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

    @overload
    def __getitem__(self, idx: int) -> Token:
        pass

    @overload
    def __getitem__(self, idx: slice) -> Iterable[Token]:
        pass

    def __getitem__(self, idx):
        return self.tokens[idx]

    def __iter__(self) -> Iterable[Token]:
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
