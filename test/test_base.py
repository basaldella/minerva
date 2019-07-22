import minerva as mine
import pytest


@pytest.fixture
def sample_text():
    return "The quick brown fox jumps over the lazy dog."


@pytest.fixture
def sentence(sample_text):
    return mine.Sentence(sample_text)


def test_tokenization(sentence, sample_text):
    assert len(sentence) == 10
    assert sentence[0].text == "The"

    last_token = sentence[len(sentence) - 1]
    assert last_token.parent == sentence
    assert last_token.text == "."
    assert last_token.char_index == sample_text.index(".")

    middle_token = sentence[4]
    assert middle_token.text == "jumps"
    assert middle_token.char_index == sample_text.index("jumps")
    assert middle_token.end_char_index == sample_text.index("jumps") + len("jumps")
