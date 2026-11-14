#!/usr/bin/env python3
"""Targeted TGT AT_074 Korean text history regression, including 2021 Holy school."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
timeline=load('data/AT_074.json')
meta=load('metadata/AT_074.json')
obs=meta['supplementalAudit']['document']['historicalTextObservations']
launch=next(x['rawText'] for x in obs if x['build']=='3.0.0.9786')
modern=next(x['rawText'] for x in obs if x['build']=='12.2.0.26996').replace('천상의_보호막','천상의 보호막')
assert list(timeline)==['2015-08-25','2018-10-03','2021-03-26']
assert timeline['2015-08-25']['text']==launch
assert timeline['2018-10-03']=={'text':modern}
assert timeline['2021-03-26']=={'spellSchool':'HOLY'}
assert meta['release']=={'date':'2015-08-25','status':'verified'}
assert meta['historicalTextCorrection']['dateConfidence']=='estimated-card-specific'
for name in ('cards.json','cards-date.json','render.json','render-date.json'):
 card=next(x for x in load(name)['cards'] if x['id']=='AT_074')
 assert card['text']==modern and card['spellSchool']=='HOLY' and card['releasedAt']=='2015-08-25',name
 for version in ('2015-08-25','2018-10-02','2018-10-03','2021-03-25','2021-03-26'):
  if not name.startswith('render'):continue
  active=[r for r in card['history'] if r.get('from','0001-01-01')<=version<r['before']]
  assert len(active)<=1,name
  state=dict(card)
  for event in active:
   for k in event['changes'].get('__remove',[]):state.pop(k,None)
   state.update({k:v for k,v in event['changes'].items() if k!='__remove'})
  expected=launch if version<'2018-10-03' else modern
  assert state['text']==expected,(name,version)
  if name.endswith('-date.json'):
   assert state.get('spellSchool')==('HOLY' if version>='2021-03-26' else None),(name,version)
for name in ('history.json','history-date.json'):
 entry=load(name)['cards']['2717']
 assert len(entry['history'])==2
 assert entry['history'][0]['before']=='2018-10-03'
 assert entry['history'][1]['before']=='2021-03-26'
assert meta['originalSource']['card']['id']=='AT_074'
print(json.dumps({'result':'pass','id':'AT_074','release':'2015-08-25',
 'wording':'2018-10-03','wordingDateConfidence':'estimated-card-specific',
 'spellSchool':'2021-03-26'},ensure_ascii=False))
