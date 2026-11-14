#!/usr/bin/env python3
"""Focused independent checks of the 23 single-boundary 12.2 TGT koKR rewrites."""
import json
from pathlib import Path
from restore_tgt_122_kokr import IDS,FIRST,WORDING_DAY,normalized

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
old={x['id']:x for x in read('cards.json')['cards']}
precise={x['id']:x for x in read('cards-date.json')['cards']}
render={x['id']:x for x in read('render-date.json')['cards']}
hist=read('history-date.json')['cards']
legacy={x['id']:x for x in read('render.json')['cards']}
old_hist=read('history.json')['cards']
for cid in IDS:
    data=read('data/'+cid+'.json');meta=read('metadata/'+cid+'.json')
    observed=meta['supplementalAudit']['document']['historicalTextObservations']
    launch=normalized(next(x['rawText'] for x in observed if x['build']=='3.0.0.9786'))
    assert next(iter(data))==FIRST and WORDING_DAY in data
    assert data[FIRST]['text']==launch
    assert set(data[WORDING_DAY])=={'text'}
    assert meta['release']['date']==FIRST
    assert meta['historicalTextCorrection']['dateConfidence']=='estimated-card-specific'
    assert precise[cid]['text']==old[cid]['text'] and render[cid]['text']==old[cid]['text']
    assert old[cid]['id']==cid and precise[cid]['dbfId']==meta['currentCatalog']['dbfId']
    assert render[cid]['history']==hist[str(old[cid]['dbfId'])]['history']
    assert legacy[cid].get('history',[])==old_hist.get(str(old[cid]['dbfId']),{}).get('history',[])
    first_day=render[cid]['history'][0]
    assert first_day['before']==WORDING_DAY and first_day['from']==FIRST
    assert first_day['changes']['text']==launch
    old_rev=legacy[cid]['history'][0]
    assert old_rev['before']==WORDING_DAY and old_rev['changes']['text']==launch
    assert old[cid]['releasedAt']==FIRST
assert len(IDS)==23
assert len(old)==len(precise)==148
print(json.dumps({'result':'pass','reviewed':len(IDS),'ids':IDS,
    'patchDayConfidence':'estimated-card-specific'},ensure_ascii=False))
