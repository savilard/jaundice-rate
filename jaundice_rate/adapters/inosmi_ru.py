from bs4 import BeautifulSoup

from jaundice_rate.adapters import html_tools
from jaundice_rate.adapters.exceptions import ArticleNotFound


def sanitize(html: str, plaintext: bool = False):
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.select_one('div.layout-article')

    if not article:
        raise ArticleNotFound()

    article.attrs = {}

    buzz_blocks = [
        *article.select('.article__notice'),
        *article.select('.article__aggr'),
        *article.select('aside'),
        *article.select('.media__copyright'),
        *article.select('.article__meta'),
        *article.select('.article__info'),
        *article.select('.article__tags'),
    ]
    for el in buzz_blocks:
        el.decompose()

    html_tools.remove_buzz_attrs(article)
    html_tools.remove_buzz_tags(article)

    if plaintext:
        html_tools.remove_all_tags(article)
        text = article.get_text()
    else:
        text = article.prettify()
    return text.strip()
