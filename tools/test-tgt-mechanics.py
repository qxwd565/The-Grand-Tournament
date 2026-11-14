#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,sys
from date_schema import *
r=Path(__file__).resolve().parents[1];e=load(r/'tools/tgt-mechanics-evidence.json');a=load(r/'tools/tgt-keyword-abilities.json');assert len(e['builds'])==46
assert sum(len(b['cards']) for b in e['builds'])==6931
for b in e['builds']:
 assert len(b['xmlSha256'])==64 and '/blob/' in b['source']
 for cid,c in b['cards'].items():assert set(c)>= {'Tag','ReferencedTag','rawText','actualMechanics'}
prior=(r/'tools/tgt-keyword-abilities.json').read_bytes();subprocess.run([sys.executable,str(r/'tools/build-keyword-abilities.py')],check=True);assert prior==(r/'tools/tgt-keyword-abilities.json').read_bytes()
def at(cid,d=None):return fold(load(r/'data'/f'{cid}.json'),d)
for cid in a['baseline']:
 if cid in ('AT_132_SHAMANa','AT_132_SHAMANb','AT_132_SHAMANc','AT_132_SHAMANd'):continue
 t=load(r/'data'/f'{cid}.json')
 for d in t:
  m=at(cid,d)['mechanics'];assert len(m)==len(set(m)) and set(m)<=set(a['vocabulary']);assert not set(m)&{'AURA','TRIGGER_VISUAL'}
  assert ('INSPIRE' in m)==('격려' in at(cid,d)['text'])
for cid in ['AT_004','AT_005','HERO_11bp2','AT_130']:assert at(cid)['mechanics']==[]
assert at('AT_005t')['mechanics']==['CHARGE']
assert at('AT_006','2023-08-22')['mechanics']==['INSPIRE'];assert at('AT_006','2023-08-23')['mechanics']==['INSPIRE','SPELLPOWER']
for cid in ['AT_012','AT_018','AT_049']:
 assert at(cid,'2023-08-22')['mechanics']==['INSPIRE'];assert at(cid,'2023-08-23')['mechanics']==['BATTLECRY','INSPIRE']
assert at('AT_011','2023-04-05')['mechanics']==['OVERHEAL']
for cid,keyword in [('AT_042a','CHARGE'),('AT_042b','STEALTH')]:assert at(cid,'2018-11-29')['mechanics']==[] and at(cid,'2018-11-30')['mechanics']==[keyword]
assert at('AT_035t','2018-10-02')['mechanics']==[] and at('AT_035t','2018-10-03')['mechanics']==['CASTS_WHEN_DRAWN']
for cid in ['AT_037','AT_042']:assert at(cid,'2015-08-25')['mechanics']==['CHOOSE_ONE']
for cid,keyword in [('AT_069','TAUNT'),('AT_051','OVERLOAD'),('AT_132','BATTLECRY')]:assert keyword in at(cid,'2018-01-01')['mechanics'] and keyword in at(cid,'2020-01-01')['mechanics']
report={'result':'pass','cards':148,'archivedBuilds':46,'tagObservations':6931,'datedKeywordChanges':sum(map(len,a['events'].values())),'scope':'Bounded intrinsic keywords; own text and behavior override misleading/missing implementation/reference tags. No invented flag-change dates.'};put(r/'tools/tgt-mechanics-validation.json',report);print(json.dumps(report))
