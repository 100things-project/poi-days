"""Offline collector integration checks; never contacts a public source."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import requests
from collector_http import fetch_public

ROOT = Path(__file__).resolve().parents[1]

def load(kind):
    spec = importlib.util.spec_from_file_location(kind, ROOT / f'scripts/fetch-{kind}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

for kind in ('rankings', 'news'):
    m = load(kind)
    previous = {'sites': {}, 'items': []}
    if kind == 'rankings':
        for sid, source in m.SOURCES.items():
            previous['sites'][sid] = {
                'name': source['name'], 'sourceUrl': source['url'], 'status': 'ok', 'stale': False,
                'checkedAt': '2026-01-01', 'fetchedAt': '2026-01-01T00:00:00+09:00',
                'items': [{'rank': i, 'title': f'前回正常案件{i}', 'rewardText': '100pt',
                           'sourceHref': source['url'] + f'?fixture={i}', 'verified': True,
                           'checkedAt': '2026-01-01', 'sample': False} for i in range(1,6)]}
    else:
        previous['items'] = [{'site': sid, 'siteName': source['name'], 'id': sid,
                              'title': '前回の正常なお知らせ', 'date': '2026-01-01',
                              'sourceUrl': source['url'], 'official': True} for sid, source in m.SOURCES.items()]
    fetch_name = 'fetch_html' if kind == 'rankings' else 'fetch'
    with tempfile.TemporaryDirectory() as tmp, patch('requests.get', side_effect=AssertionError('network forbidden in offline test')):
        m.OUT = Path(tmp) / 'snapshot.json'
        for scenario in ('403', 'timeout', 'zero', 'structure'):
            def response(*args):
                if scenario == '403':
                    raise requests.HTTPError('HTTP 403 fixture')
                if scenario == 'timeout':
                    raise requests.Timeout('timeout fixture')
                return '' if scenario == 'zero' else '<html><a href="https://evil.test/">Changed layout 999pt</a></html>'
            setattr(m, fetch_name, response)
            for prior in (previous, {'sites': {}, 'items': []}):
                m.OUT.write_text(json.dumps(prior))
                with contextlib.redirect_stdout(io.StringIO()):
                    assert m.main() == 0
                result = json.loads(m.OUT.read_text())
                if kind == 'rankings':
                    for sid, state in result['sites'].items():
                        old = prior.get('sites', {}).get(sid)
                        assert state['status'] == ('stale' if old else 'unavailable'), (kind, scenario, sid)
                        assert state['items'] == (old['items'] if old else [])
                        if old:
                            assert state['checkedAt'] == old['checkedAt']
                            assert state['fetchedAt'] == old['fetchedAt']
                else:
                    assert sorted(result['items'], key=lambda n: n['id']) == sorted(prior.get('items', []), key=lambda n: n['id'])
                    assert all(s['status'] == ('stale' if prior.get('items') else 'unavailable') for s in result['sources'].values())
        # One successful source must refresh while other failures remain isolated.
        if kind == 'rankings':
            fixture = '<ol data-ga-action="クリック - 総合">' + ''.join(
                f'<li><a class="block__link" href="/ad/{i}"><h2 class="a-list__item__title">正常案件{i}</h2><em class="a-list__item__point">{i}pt</em></a></li>' for i in range(5)) + '</ol>'
            success = 'moppy'
        else:
            fixture = '<div><a href="/notifications/detail/id/999">正常なお知らせのタイトル</a><div class="message_date">2026-09-10</div></div>'
            success = 'hapitas'
        def isolated(url):
            if url == m.SOURCES[success]['url']:
                return fixture
            raise requests.Timeout('isolated source failure')
        setattr(m, fetch_name, isolated)
        m.OUT.write_text(json.dumps(previous))
        with contextlib.redirect_stdout(io.StringIO()):
            assert m.main() == 0
        result = json.loads(m.OUT.read_text())
        states = result['sites'] if kind == 'rankings' else result['sources']
        assert states[success]['status'] == 'ok'
        assert all(state['status'] == 'stale' for sid, state in states.items() if sid != success)
        if kind == 'rankings':
            good_fixture = fixture
            for invalid_fixture in (good_fixture.replace('/ad/1', '/ad/0'), good_fixture.replace('/ad/0', 'https://evil.test/ad/0')):
                fixture = invalid_fixture
                m.OUT.write_text(json.dumps(previous))
                with contextlib.redirect_stdout(io.StringIO()):
                    assert m.main() == 0
                result = json.loads(m.OUT.read_text())
                assert result['sites']['moppy']['status'] == 'stale'
                assert result['sites']['moppy']['items'] == previous['sites']['moppy']['items']
    print(f'PASS: {kind}: four-source 403/timeout/zero/structure, exact previous retention, no-prior fallback, isolated success')

# Verify actual HTTP wrapper stops at denial/timeout and never follows external redirects.
for exc in (requests.HTTPError('403'), requests.Timeout('timeout')):
    with patch('requests.get', side_effect=exc) as get:
        try:
            fetch_public('https://example.com/public', 'offline-test')
        except (requests.HTTPError, requests.Timeout):
            pass
        else:
            raise AssertionError('expected HTTP failure')
        assert get.call_count == 1
r = requests.Response();r.status_code = 302;r.headers['Location'] = 'https://evil.test/private'
with patch('requests.get', return_value=r) as get:
    try:
        fetch_public('https://example.com/public', 'offline-test')
    except RuntimeError:
        pass
    else:
        raise AssertionError('cross-origin redirect accepted')
    assert get.call_count == 1
print('PASS: bounded GET, no retry after denial/timeout, no cross-origin redirect')
