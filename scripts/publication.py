"""Save and deploy only validated current-main output. No network collection here."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ['content/live-rankings.json', 'content/live-news.json', 'docs', 'dist']


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def verify():
    inventories = []
    for name in ('docs', 'dist'):
        inventory = {}
        for path in (ROOT / name).rglob('*'):
            if path.is_symlink():
                raise RuntimeError('publication contains a symbolic link')
            if path.is_file():
                if path.stat().st_nlink != 1:
                    raise RuntimeError('publication contains a hard link')
                relative = path.relative_to(ROOT / name)
                if any(part in {'.qa', '.git', 'node_modules', '__pycache__'} for part in relative.parts):
                    raise RuntimeError('non-public files in publication')
                inventory[str(relative)] = path.read_bytes()
        if not inventory.get('index.html'):
            raise RuntimeError('publication has no index')
        inventories.append(inventory)
    if inventories[0] != inventories[1]:
        raise RuntimeError('docs and dist differ')


def current():
    remote = git('ls-remote', '--exit-code', 'origin', 'refs/heads/main').split()[0]
    if remote != git('rev-parse', 'HEAD'):
        raise RuntimeError('main changed; stop without rebase, force-push or stale deployment')


def save():
    current()
    git('add', '--', *OUTPUTS)
    staged = git('diff', '--cached', '--name-only').splitlines()
    if any(not (p in OUTPUTS or p.startswith(('docs/', 'dist/'))) for p in staged):
        raise RuntimeError('unexpected staged source changes')
    if not staged:
        print('No generated changes to save; publication can still recover a failed deploy.')
        return
    git('-c', 'user.name=github-actions[bot]', '-c',
        'user.email=41898282+github-actions[bot]@users.noreply.github.com',
        'commit', '-m', 'Refresh validated POI DAYS data and site')
    # A racing human push is rejected normally. Never force-push or merge stale output.
    git('push', 'origin', 'HEAD:refs/heads/main')


if __name__ == '__main__':
    {'verify': verify, 'save': save, 'current': current}[sys.argv[1]]()
