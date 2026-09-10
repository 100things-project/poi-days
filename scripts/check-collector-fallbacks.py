"""Offline regression: denied sources never erase the last good snapshot."""
import importlib.util,json,tempfile,contextlib,io
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for kind in ('rankings','news'):
 spec=importlib.util.spec_from_file_location(kind,root/f'scripts/fetch-{kind}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 real=json.loads((root/f'content/live-{kind}.json').read_text())
 def fail(*args):raise RuntimeError('HTTP 403 fixture; no retry/bypass')
 if kind=='rankings':m.fetch_html=fail
 else:m.fetch=fail
 with tempfile.TemporaryDirectory() as tmp:
  m.OUT=Path(tmp)/'state.json'
  # Each source is exercised with good previous data and without any previous data.
  if kind=='rankings':
   previous=json.loads(json.dumps(real));good=real['sites']['moppy']
   for sid in m.SOURCES:previous['sites'][sid]=dict(good,name=m.SOURCES[sid]['name'])
  else:
   previous=json.loads(json.dumps(real));good=real['items'][0]
   previous['items']=[dict(good,site=sid,id=sid) for sid in m.SOURCES]
  for old in (previous,{'sites':{},'items':[]}):
   m.OUT.write_text(json.dumps(old))
   with contextlib.redirect_stdout(io.StringIO()):assert m.main()==0
   result=json.loads(m.OUT.read_text())
   if kind=='rankings':
    for sid,state in result['sites'].items():
     assert state['status']==('stale' if old.get('sites') else 'unavailable')
     assert state['items']==(old['sites'][sid]['items'] if old.get('sites') else [])
   else:
    assert sorted(result['items'],key=lambda n:n['id'])==sorted(old.get('items',[]),key=lambda n:n['id'])
    assert all(s['status']==('stale' if old.get('items') else 'unavailable') for s in result['sources'].values())
 print(kind, 'PASS: four-source 403 keeps exact previous data; missing prior data stays unavailable; offline only')
