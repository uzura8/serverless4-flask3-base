import fast_ulid
import re
import string
import random
import uuid
from typing import Iterator
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        # Add codes hear if you need
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_html_tags(html_str):
    s = MLStripper()
    s.feed(html_str)
    return s.get_data()


def strip_html_tags_simple(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def _parse_words(val: str) -> Iterator[str]:
    for block in re.split(r'[ _-]+', val):
        yield block


def to_pascal_case(val: str) -> str:
    words_iter = _parse_words(val)
    return ''.join(word.capitalize() for word in words_iter)


def to_camel_case(val: str) -> str:
    words_iter = _parse_words(val)
    try:
        first = next(words_iter)
    except StopIteration:
        return ''
    return first.lower() + ''.join(word.capitalize() for word in words_iter)


def to_snake_case(val: str) -> str:
    words_iter = _parse_words(val)
    return '_'.join(word.lower() for word in words_iter)


def to_kebab_case(val: str) -> str:
    words_iter = _parse_words(val)
    return '-'.join(word.lower() for word in words_iter)


def random_str(num, is_digits_only=False):
    if is_digits_only:
        population = string.digits
    else:
        population = string.ascii_letters + string.digits

    return ''.join(random.choices(population, k=num))


def new_uuid(fmt='ulid'):
    """
    Generate a new UUID string.
    :param fmt: str, 'ulid' or 'uuidv4' or 'firebase_uid'
    :return: str, UUID string
    """
    if fmt == 'ulid':
        return fast_ulid.ulid().lower()

    if fmt == 'uuidv4':
        return str(uuid.uuid4()).replace('-', '').lower()

    res = str(uuid.uuid4()).replace('-', '')
    if fmt == 'firebase_uid':
        return res[:28]
    return res


def validate_uuid(val, fmt='ulid'):
    if fmt == 'ulid':
        pattern = r'^0[0-2][0-9a-hjkmnp-tv-z]{24}$'

    elif fmt == 'uuidv4':
        pattern = r'^[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}$'

    else:
        raise ValueError('Invalid format')

    return re.match(pattern, val) is not None


def validate_username(text):
    regexp = r'^[0-9a-zA-Z_]{2,15}$'
    return re.match(regexp, text) is not None


def validate_slug(val, is_random_generated=False, maxlen=128):
    if is_random_generated:
        pattern = r'^[0-9a-zA-Z_\-]{1,' + str(maxlen) + '}$'
    else:
        pattern = r'^[0-9a-z\-]{1,' + str(maxlen) + '}$'
    return re.match(pattern, val) is not None


def validate_email(email):
    email = email.strip()
    if not email:
        return False

    pattern = '^([_a-z0-9-]+(\.[_a-z0-9-]+)*)' +\
        '@([a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4}))$'
    return re.findall(pattern, email)


def validate_url(url):
    return re.match('^https?://[\w\-\.\!~\*\'\(\);\/\?\:@&=+\$,%#]+$', url)


def nl2br(text):
    return text.replace('\n', '<br>\n')


def url2link(text):
    ptn = r'(https?://[0-9a-zA-Z\-\.\!~\*\'\(\);\/\?\:@&=+\$,%#]+)'
    return re.sub(ptn, r'<a href="\1" target="_blank">\1</a>', text)
