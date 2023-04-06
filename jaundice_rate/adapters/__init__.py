from . import inosmi_ru
from .exceptions import ArticleNotFoundError

__all__ = ['SANITIZERS', 'ArticleNotFoundError']

SANITIZERS = {
    'inosmi.ru': inosmi_ru.sanitize,
}
