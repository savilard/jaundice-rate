import pymorphy2
import pytest


@pytest.fixture()
def morph():
    return pymorphy2.MorphAnalyzer()


@pytest.fixture()
def charged_words():
    return ['во-первых', 'хотеть', 'чтобы']
