import string

import anyio
from async_timeout import timeout


def _clean_word(word):
    word = word.replace('«', '').replace('»', '').replace('…', '')
    word = word.strip(string.punctuation)
    return word


async def split_by_words(morph, text):
    """Takes into account punctuation marks, case and word forms, and throws out prepositions."""
    words = []
    async with anyio.fail_after(3):
        for word in text.split():
            cleaned_word = _clean_word(word)
            normalized_word = morph.parse(cleaned_word)[0].normal_form
            if len(normalized_word) > 2 or normalized_word == 'не':
                words.append(normalized_word)
            await anyio.sleep(0)
    return words


def calculate_jaundice_rate(article_words, charged_words):
    """Calculates text jaundice, takes a list of "charged" words and searches for them inside article_words."""
    if not article_words:
        return 0.0

    found_charged_words = [word for word in article_words if word in set(charged_words)]
    score = len(found_charged_words) / len(article_words) * 100

    return round(score, 2)


