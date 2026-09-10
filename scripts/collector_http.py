"""Bounded public GETs: no authentication, retries or cross-origin redirects."""
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


def official_url(base, value):
    try:
        a, b = urlparse(base), urlparse(value)
        return (b.scheme == 'https' and bool(a.hostname) and b.hostname == a.hostname
                and b.username is None and b.password is None and b.port in (None, 443))
    except (ValueError, TypeError):
        return False


def fetch_public(url, user_agent, timeout=15, minimum=500):
    current = url
    for _ in range(3):
        if not official_url(url, current):
            raise RuntimeError('unsafe public source URL')
        response = requests.get(current, headers={'User-Agent': user_agent, 'Accept-Language': 'ja,en;q=0.7'},
                                timeout=timeout, allow_redirects=False)
        if response.status_code in (301, 302, 303, 307, 308):
            current = urljoin(current, response.headers.get('Location', ''))
            continue
        response.raise_for_status()
        if len(response.content) < minimum:
            raise RuntimeError('empty or undersized public response')
        return BeautifulSoup(response.content, 'html.parser').decode()
    raise RuntimeError('too many public source redirects')
