import pymorphy2
import pytest


@pytest.fixture()
def morph():
    return pymorphy2.MorphAnalyzer()
