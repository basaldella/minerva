import minerva as mine
import pytest


@pytest.fixture(
    scope="module",
    params=[
        "The quick brown fox jumps over the lazy dog.",
        "The quick brown fox\tjumps over the lazy dog.",
        "The quick brown fox   jumps \n   over\t   the lazy dog\t     .",
    ],
)
def sample_text(request):
    return request.param


@pytest.fixture
def sample_tokens():
    return ["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog", "."]


@pytest.fixture
def sample_pos_tags():
    return ["DT", "JJ", "NN", "NN", "VBZ", "IN", "DT", "JJ", "NN", "."]


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

    assert sentence.token_at_char(sample_text.index("The")).text == "The"
    assert sentence.token_at_char(sample_text.index("The") + 2).text == "The"
    assert sentence.token_at_char(sample_text.index("jumps") + 1).text == "jumps"
    assert sentence.token_at_char(sample_text.index("lazy")).text == "lazy"
    assert (
        sentence.token_at_char(sample_text.index("lazy") + len("lazy") - 1).text
        == "lazy"
    )
    assert sentence.token_at_char(len(sample_text) - 1).text == "."
    assert not sentence.token_at_char(3)
    assert not (sentence.token_at_char(sample_text.index("the") + len("the")))
    assert not (sentence.token_at_char(sample_text.index("lazy") + len("lazy")))


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


def test_tags(sentence, sample_pos_tags):

    for i, token in enumerate(sentence):
        token["pos"] = mine.Annotation(sample_pos_tags[i])

    annos = [anno.value for anno in sentence.get_annotation("pos")]
    assert annos == sample_pos_tags

    sentence.add_annotation("test-key", "test-value-1", begin=1, end=4, score=0.5)
    for t in sentence[1:4]:
        assert t["test-key"].value == "test-value-1"

    with pytest.raises(IndexError):
        assert sentence.add_annotation(
            "test-key", "test-value-2", begin=8, end=11, score=1
        )

    sentence.add_annotation("test-key", "test-value-2", begin=7, end=9, score=1)
    for t in sentence[7:9]:
        assert t["test-key"].value == "test-value-2"

    spans = sentence.get_annotation("test-key")
    assert spans[0].text == "quick brown fox"
    assert spans[1].text == "lazy dog"
