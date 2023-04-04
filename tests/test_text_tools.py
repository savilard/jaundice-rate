import pymorphy2
import pytest

from jaundice_rate import text_tools


@pytest.mark.asyncio
async def test_split_by_words():
    morph = pymorphy2.MorphAnalyzer()

    assert await text_tools.split_by_words(morph, 'Во-первых, он хочет, чтобы') == ['во-первых', 'хотеть', 'чтобы']
    assert await text_tools.split_by_words(morph, '«Удивительно, но это стало началом!»') == ['удивительно', 'это',
                                                                                              'стать', 'начало']


def test_calculate_jaundice_rate():
    assert -0.01 < text_tools.calculate_jaundice_rate([], []) < 0.01
    assert 33.0 < text_tools.calculate_jaundice_rate(['все', 'аутсайдер', 'побег'], ['аутсайдер', 'банкротство']) < 34.0
