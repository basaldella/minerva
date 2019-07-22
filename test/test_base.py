import minerva as mine
import pytest


@pytest.fixture(scope="module")
def sample_text():
    return "The quick brown fox jumps over the lazy dog."


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
