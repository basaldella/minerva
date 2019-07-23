import minerva as mine
import pytest


@pytest.fixture(scope="module")
def sample_text():
    return "The quick brown fox jumps over the lazy dog."


@pytest.fixture
def sample_tokens():
    return ["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog", "."]


@pytest.fixture(scope="module")
def lipsum_array():
    return [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
        + "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    ]


@pytest.fixture
def lipsum_txt():
    return (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
        "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n"
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
    )


@pytest.fixture(scope="module")
def sentence(sample_text):
    return mine.Sentence(sample_text)


def test_tokenization(sentence, sample_text, sample_tokens):
    assert len(sentence) == 10
    assert sentence[0].text == "The"

    for i, token in enumerate(sentence):
        assert token.parent == sentence
        assert token.text == sample_tokens[i]
        assert token.char_index == sample_text.index(sample_tokens[i])

    middle_token = sentence[4]
    assert middle_token.text == "jumps"
    assert middle_token.char_index == sample_text.index("jumps")
    assert middle_token.end_char_index == sample_text.index("jumps") + len("jumps")

    assert sentence.token_at_char(0).text == "The"
    assert sentence.token_at_char(2).text == "The"
    assert sentence.token_at_char(23).text == "jumps"
    assert sentence.token_at_char(35).text == "lazy"
    assert sentence.token_at_char(38).text == "lazy"
    assert sentence.token_at_char(len(sample_text) - 1).text == "."
    assert not sentence.token_at_char(3)
    assert not sentence.token_at_char(34)
    assert not sentence.token_at_char(39)


def test_document(lipsum_array, lipsum_txt):
    d1 = mine.Document(lipsum_txt)
    d2 = mine.Document(lipsum_array)

    assert len(d1) == len(d2) == 2
    for i in range(len(d1)):
        assert d1[i].text == d2[i].text
        assert d1[i].index == d2[i].index == i
        for j in range(len(d1[i])):
            assert d1[i][j].text == d2[i][j].text

    assert d1[0].text == lipsum_array[0]
    assert d1.text == d2.text
    assert d1.text == lipsum_txt


def test_corpus(lipsum_array):

    sentences = [mine.Sentence(lipsum) for lipsum in lipsum_array]

    c1 = mine.Corpus("1", items=sentences)
    c2 = mine.Corpus("2")
    for sentence in sentences:
        c2.add(sentence)

    assert len(c1) == len(c2) == len(sentences)
    assert c1[0].text == c2[0].text

    c3 = c1 + c2
    assert len(c3) == len(c1) + len(c2)
    assert c3[0] == c1[0]
    assert c3[-1] == c2[-1]
