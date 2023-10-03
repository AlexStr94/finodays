from cashbacker.casbacker import get_n_most_frequent_strings


def test_get_n_most_frequent_strings():
    assert get_n_most_frequent_strings(["a", "b", "c"], 2) == ["a", "b"]


def test_cashbacker_tokenize_text(get_cashbacker):
    products = ["Sample product in English.", "Пример товара на русском языке."]
    padded_sequences = get_cashbacker.tokenize_text(products)
    assert padded_sequences.shape == (len(products), 21)


def test_cashbacker_preprocess_sentences(get_cashbacker):
    sentences = ["This is a test sentence.", "Another test sentence."]
    max_length = 10
    padded_sequences = get_cashbacker.preprocess_sentences(sentences, max_length)
    assert padded_sequences.shape == (len(sentences), max_length)


def test_get_topics_name(get_cashbacker):
    product_names = ["Sample product in English.", "Пример товара на русском языке."]
    topics = get_cashbacker.get_topics_name(product_names)
    assert len(topics) == len(product_names)
