"""Offline workflow contract plus real temporary-Git race/retention tests."""
from pathlib import Path
import importlib.util
import shutil
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('publication', ROOT / 'scripts/publication.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
workflows = list((ROOT / '.github/workflows').glob('*.yml'))
assert len(workflows) == 1, 'duplicate workflows could collect or publish twice'
w = yaml.load(workflows[0].read_text(), Loader=yaml.BaseLoader)
assert set(w['on']) == {'schedule', 'push', 'workflow_dispatch'}
assert w['on']['schedule'] == [{'cron': '5 21 * * *'}]
assert w['on']['push']['branches'] == ['main']
assert w['concurrency']['cancel-in-progress'] == 'false'
job = w['jobs']['publish']
assert "github.ref == 'refs/heads/main'" in job['if']
assert "github.repository == '100things-project/poi-days'" in job['if']
assert job['environment']['name'] == 'github-pages'
assert job['permissions'] == {'contents':'write','pages':'write','id-token':'write'}
steps = job['steps']
collect = next(s for s in steps if 'python scripts/fetch-rankings.py' in s.get('run',''))
assert collect['if'] == "github.event_name == 'schedule'"
assert collect['run'].count('python scripts/fetch-rankings.py') == 1
assert collect['run'].count('python scripts/fetch-news.py') == 1
assert next(s for s in steps if s.get('uses','').startswith('actions/checkout@'))['with'] == {'ref':'main'}
assert any('git fetch --no-tags --depth=1 origin 4d204' in s.get('run','') for s in steps)
order = '\n'.join(s.get('run',s.get('uses','')) for s in steps)
markers = ['python scripts/check-publication.py','python scripts/fetch-rankings.py',
 'python check.py','python scripts/check-recommendation.py','python scripts/publication.py verify',
 'python scripts/publication.py save','actions/upload-pages-artifact@','python scripts/publication.py current','actions/deploy-pages@']
assert [order.index(s) for s in markers] == sorted(order.index(s) for s in markers)
assert next(s for s in steps if s.get('uses','').startswith('actions/upload-pages-artifact@'))['with']['path'] == 'docs'
assert not any(s.get('if') in ('always()', '${{ always() }}') for s in steps)
assert 'workflow_run' not in w['on'] and 'repository_dispatch' not in w['on']
print('PASS: single schedule; main-only; no collection on push/manual; validate-save-upload-current-deploy path; no recursive trigger')

def run(*args, cwd=None):
    return subprocess.check_output(args,cwd=cwd,stderr=subprocess.STDOUT,text=True).strip()

def expect_failure(fn):
    try: fn()
    except (RuntimeError,subprocess.CalledProcessError): return
    raise AssertionError('unsafe operation succeeded')

with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp);remote=p/'remote.git';local=p/'local';other=p/'other'
    run('git','init','--bare','--initial-branch=main',str(remote))
    run('git','clone',str(remote),str(local))
    for key,val in [('user.name','Offline Test'),('user.email','test@example.invalid')]:
        run('git','config',key,val,cwd=local)
    for folder in ('docs','dist','content'): (local/folder).mkdir()
    for folder in ('docs','dist'): (local/folder/'index.html').write_text('old')
    for file in ('live-rankings.json','live-news.json'): (local/'content'/file).write_text('{}')
    run('git','add','.',cwd=local);run('git','commit','-m','baseline',cwd=local)
    run('git','push','origin','main',cwd=local)
    m.ROOT=local
    m.verify();m.current();m.save() # No-change recovery deploy remains possible.
    for folder in ('docs','dist'): (local/folder/'index.html').write_text('validated new')
    m.verify();m.save();m.current()
    assert run('git','show','main:docs/index.html',cwd=remote)=='validated new'
    # Mismatched/QA/symlink artifacts are rejected before upload.
    (local/'dist/index.html').write_text('bad');expect_failure(m.verify)
    (local/'dist/index.html').write_text('validated new')
    (local/'docs/.qa').mkdir();(local/'docs/.qa/test.html').write_text('test');expect_failure(m.verify)
    shutil.rmtree(local/'docs/.qa')
    (local/'docs/link').symlink_to(local/'docs/index.html');expect_failure(m.verify);(local/'docs/link').unlink()
    # A human update between validation and save/deploy must survive unchanged.
    run('git','clone',str(remote),str(other))
    run('git','config','user.name','Other',cwd=other);run('git','config','user.email','other@example.invalid',cwd=other)
    (other/'article.txt').write_text('human edit')
    run('git','add','.',cwd=other);run('git','commit','-m','human update',cwd=other);run('git','push',cwd=other)
    remote_sha=run('git','rev-parse','main',cwd=remote)
    expect_failure(m.current);expect_failure(m.save)
    assert run('git','rev-parse','main',cwd=remote)==remote_sha
    assert run('git','show','main:article.txt',cwd=remote)=='human edit'
    # Race after the pre-save check: normal push must reject, never overwrite.
    run('git','fetch','origin','main',cwd=local)
    run('git','reset','--hard','FETCH_HEAD',cwd=local)
    for folder in ('docs','dist'): (local/folder/'index.html').write_text('racing build')
    original_git=m.git
    def race_git(*args):
        if args[0]=='push':
            (other/'article.txt').write_text('newer human edit')
            run('git','add','.',cwd=other);run('git','commit','-m','racing human update',cwd=other)
            run('git','push',cwd=other)
        return original_git(*args)
    m.git=race_git
    expect_failure(m.save)
    assert run('git','show','main:article.txt',cwd=remote)=='newer human edit'
    assert run('git','show','main:docs/index.html',cwd=remote)=='validated new'
print('PASS: real local Git save/no-change/concurrent-main/push-race guards; unchanged human data; artifact mismatch/QA/symlink rejection; no external network')
