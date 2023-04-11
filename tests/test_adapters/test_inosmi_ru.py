import httpx
import pytest

import jaundice_rate


def test_sanitize():
    with httpx.Client(follow_redirects=True) as client:
        resp = client.get('https://inosmi.ru/economic/20190629/245384784.html')
    resp.raise_for_status()
    clean_text = jaundice_rate.sanitize(resp.text)

    assert 'В субботу, 29 июня, президент США Дональд Трамп' in clean_text
    assert 'За несколько часов до встречи с Си' in clean_text

    assert '<img src="' in clean_text
    assert '<h1>' in clean_text

    clean_plaintext = jaundice_rate.sanitize(resp.text, plaintext=True)

    assert 'В субботу, 29 июня, президент США Дональд Трамп' in clean_plaintext
    assert 'За несколько часов до встречи с Си' in clean_plaintext

    assert '<img src="' not in clean_plaintext
    assert '<a href="' not in clean_plaintext
    assert '<h1>' not in clean_plaintext
    assert '</article>' not in clean_plaintext
    assert '<h1>' not in clean_plaintext


def test_sanitize_wrong_url():
    with httpx.Client(follow_redirects=True) as client:
        resp = client.get('http://example.com')
    resp.raise_for_status()
    with pytest.raises(jaundice_rate.ArticleNotFoundError):
        jaundice_rate.sanitize(resp.text)
