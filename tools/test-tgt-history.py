#!/usr/bin/env python3
"""Check TGT release baselines, Korean dates, observations and all generated formats."""
from pathlib import Path
from datetime import date,timedelta
import copy,hashlib,importlib.util,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1]
def load(p):
 q=R/p
 if p in ('cards.json','render.json','history.json','release-policy.json','manifest.json'):q=R/'tools/supplemental-audit'/p
 if p=='data/history.json':q=R/'tools/supplemental-audit/history-date-first.json'
 return json.loads(q.read_text())
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
spec=importlib.util.spec_from_file_location('builder',R/'tools/wrapper_api_reference.py');B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
F=load('tools/tgt-current-fixtures.json');fixtures=F['cards'];obs=load('tools/tgt-client-numeric.json')['cards']
current={c['id']:c for c in load('cards.json')['cards']};render={c['id']:c for c in load('render.json')['cards']};legacy=load('history.json')['cards']
docs={p.stem:json.loads(p.read_text()) for p in (R/'tools/supplemental-audit').glob('*.json') if p.name.startswith(('AT_','OG_','HERO_'))}
audit=load('tools/tgt-release-audit.json');policy=load('release-policy.json');aggregate=load('data/history.json');manifest=load('manifest.json')
assert len(docs)==152 and set(docs)==set(current)==set(render)==set(fixtures)==set(obs)
assert sum(c['collectible'] for c in current.values())==132 and current['AT_063t']['collectible']
for p in R.rglob('*.json'):json.loads(p.read_text())
assert hashlib.sha256((R/'tools/original-date-first-history.json').read_bytes()).hexdigest()==F['originalDateFirstHistorySHA256']
def norm(s):return re.sub(r'<br\s*/?>\s*(?:</br\s*>)?|</br\s*>|\\r\\n|\\n|/n|\r\n|[\r\n]','<br></br>',s,flags=re.I)
def display(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k in ('nativeTags','nativeRawText'):continue
   if k in ('name','text','flavor') and isinstance(v,str):assert norm(v)==v,(k,v)
   else:display(v)
 elif isinstance(x,list):
  for v in x:display(v)
def comparable(t):return re.sub(r'\s+','',norm(t).replace('<br></br>','').replace('[x]','').replace('$','').replace('_','').replace('#','').replace('&','').replace('{0}','1/1'))
def fields(c):
 s={k:copy.deepcopy(c[k]) for k in B.SPEC_FIELDS if k in c};s['legacyArt']=c.get('legacyArt',False);return s

def forward(c,day):
 if day<c['releasedAt']:return None
 s=fields(c)
 for p in c['patches']:
  if p['date']<=day:s.update(p['changes'])
 return s

def reverse(c,day):
 if day<c['releasedAt']:return None
 s=fields(c);found=[h for h in c.get('history',[]) if ('from' not in h or h['from']<=day) and ('before' not in h or day<h['before'])]
 assert len(found)<=1,(c['id'],day)
 for h in found:s.update(h['changes'])
 return s

def date_first(cid,day):
 s=None
 for d,entries in aggregate['events'].items():
  if d>day:break
  if cid in entries:
   if s is None:s=fields(entries[cid])
   else:s.update(entries[cid])
 return s
checks=0
tribes={2:'DRAENEI',11:'UNDEAD',14:'MURLOC',15:'DEMON',17:'MECHANICAL',18:'ELEMENTAL',20:'BEAST',21:'TOTEM',23:'PIRATE',24:'DRAGON'}
classes={0:'NEUTRAL',1:'DEATHKNIGHT',12:'NEUTRAL',2:'DRUID',3:'HUNTER',4:'MAGE',5:'PALADIN',6:'PRIEST',7:'ROGUE',8:'SHAMAN',9:'WARLOCK',10:'WARRIOR'}
types={3:'HERO',4:'MINION',5:'SPELL',7:'WEAPON',10:'HERO_POWER'}
schools={0:'',1:'ARCANE',2:'FIRE',3:'FROST',4:'NATURE',5:'HOLY',6:'SHADOW',7:'FEL'}
def ver(s):return tuple(map(int,s.split('.')))
for cid,doc in docs.items():
 c=doc['card'];f=fixtures[cid]
 assert doc['schemaVersion']==2 and 'history' not in c and c['initialSpecStatus']=='partially_verified'
 assert c['releasedAt']==current[cid]['releasedAt']==policy['cards'][cid]['date']
 assert c['releaseStatus']==current[cid]['releaseStatus']=='verified'
 assert c['dbfId']==current[cid]['dbfId']==f['dbfId']
 assert digest({k:c.get(k) for k in ('nativeTags','nativeRawText')})==f['nativeSourceHash'],cid
 assert digest(current[cid].get('nativeTags'))==f['currentNativeTagsHash'],cid
 assert digest(doc['historicalTextObservations'])==f['historicalTextObservationsHash'],cid
 assert digest(current[cid])==f['expectedNormalizedCurrentHash'],('unexpected current change',cid)
 for card in (c,current[cid],render[cid]):display(card)
 latest=doc['historicalTextObservations'][-1]
 assert latest.get('lastObservedBuild',latest['build'])=='37.0.2.256589'
 assert latest['name']==current[cid]['name'] and comparable(latest['rawText'])==comparable(current[cid]['text']),cid
 B.read_patches(c,cid)
 assert all(p['date'] in c['patchSources'] for p in c['patches'])
 dates={c['releasedAt'],'2026-11-09','2099-12-31'}|{p['date'] for p in c['patches']}
 for d in dates:
  for offset in (-1,0,1):
   day=(date.fromisoformat(d)+timedelta(days=offset)).isoformat();s=forward(c,day)
   assert s==reverse(render[cid],day)==date_first(cid,day),(cid,day);checks+=1
 assert legacy.get(str(c['dbfId']),{}).get('history',[])==render[cid].get('history',[])
 assert forward(c,'2099-12-31')==reverse(current[cid],'2099-12-31')
 first=obs[cid][0];assert first[0]==('5.0.0.12574' if cid=='OG_044c' else '25.0.0.158725' if cid.startswith('HERO_11') else '3.0.0.9786')
 for o in obs[cid]:
  build=ver(o[0]);state=fields(c)
  for p in c['patches']:
   source_build=audit['eventBuilds'][cid][p['date']]
   if ver(source_build)<=build:state.update(p['changes'])
  rawnums=o[1:5].copy()
  if o[6]==7:rawnums[2]=rawnums[3]=o[4] or o[3]
  assert [state[k] for k in ('cost','attack','health','durability')]==rawnums,(cid,o[0],rawnums,state)
  assert state['type']==types[o[6]],(cid,o[0])
  races=([tribes[o[5]]] if o[5] else [])+(['UNDEAD'] if o[10] else [])
  assert state['races']==races,(cid,o[0],races,state['races'])
  assert state['spellSchool']==schools[o[11]],(cid,o[0])
  assert c['collectible']==bool(o[9])
  if cid not in ['AT_037a','AT_037b','AT_037t']:assert state['cardClass']==classes[o[8]],(cid,o[0],state['cardClass'],classes[o[8]])
  if cid not in ['AT_037','AT_042a','AT_042b']:
   assert c['rarity']=={0:None,1:'COMMON',2:'FREE',3:'RARE',4:'EPIC',5:'LEGENDARY'}[o[7]],(cid,o[0],c['rarity'],o[7])
 # Explicit first numeric proof, independently of any later patch ordering.
 initial=first[1:5].copy()
 if first[6]==7:initial[2]=initial[3]=first[4] or first[3]
 assert [c[k] for k in ('cost','attack','health','durability')]==initial
 assert c['type']==types[first[6]]

def at(cid,d):return forward(docs[cid]['card'],d)
assert at('AT_024','2015-09-29')['races']==['DEMON'] and at('AT_024','2015-09-30')['races']==[]
assert at('AT_024','2023-04-04')['spellSchool']=='FEL' and at('AT_024','2023-04-05')['spellSchool']=='SHADOW'
assert at('AT_005t','2023-07-25')['cardClass']=='NEUTRAL' and at('AT_005t','2023-07-26')['cardClass']=='MAGE'
assert at('AT_012','2023-08-22')['cost']==4 and at('AT_012','2023-08-22')['health']==4
assert at('AT_012','2023-08-23')['cost']==5 and at('AT_012','2023-08-23')['health']==4
assert at('AT_012','2023-09-06')['health']==4 and at('AT_012','2023-09-07')['health']==5
assert at('AT_025','2023-08-22')['cost']==6 and at('AT_025','2023-08-23')['cost']==3 and at('AT_025','2023-09-29')['cost']==4
assert '+1/+1' in at('AT_021','2023-08-22')['text'] and '+2/+2' in at('AT_021','2023-08-23')['text'] and '+2/+1' in at('AT_021','2023-09-29')['text']
assert '(5)' in at('AT_051','2023-09-28')['text'] and '(2)' in at('AT_051','2023-09-29')['text']
assert at('AT_045','2018-10-18')['cost']==9 and at('AT_045','2018-10-19')['cost']==10 and at('AT_045','2023-08-23')['cost']==9
assert at('AT_043','2026-04-02')['cost']==4 and at('AT_043','2026-04-03')['cost']==5
assert at('AT_036t','2016-08-09')['cost']==3 and at('AT_036t','2016-08-10')['cost']==4
assert '기본' not in at('AT_046','2016-10-03')['text'] and '기본' in at('AT_046','2016-10-04')['text']
assert '턴이 끝날 때' not in at('AT_019','2017-08-08')['text'] and '턴이 끝날 때' in at('AT_019','2017-08-09')['text']
assert at('AT_035t','2017-12-06')['cost']==0 and at('AT_035t','2017-12-07')['cost']==3
assert '뽑을 때 시전' not in at('AT_035t','2018-10-02')['text'] and '뽑을 때 시전' in at('AT_035t','2018-10-03')['text']
assert at('AT_042a','2018-11-29')['type']=='SPELL' and at('AT_042a','2018-11-30')['type']=='MINION'
assert at('AT_042t','2015-08-25')['name']=='칼날이빨 사자' and at('AT_042t','2018-11-30')['name']=='칼날이빨의 드루이드'
assert at('AT_037a','2019-04-05')['name']=='움켜쥐는 뿌리' and at('AT_037a','2019-05-15')['cost']==1
assert at('AT_132_SHAMANa','2019-02-05')['cost']==0 and at('AT_132_SHAMANa','2019-02-06')['cost']==1
assert at('AT_132','2024-03-11')['cost']==6 and at('AT_132','2024-03-12')['cost']==5 and at('AT_132','2024-03-12')['health']==4
assert at('AT_064','2022-08-16')['cost']==3 and at('AT_064','2022-08-17')['cost']==2
assert '+1' in at('AT_075','2022-08-16')['text'] and '+2' in at('AT_075','2022-08-17')['text'] and '도발' in at('AT_075','2022-08-17')['text']
assert at('AT_011','2023-04-04')['cost']==4 and at('AT_011','2023-04-05')['cost']==2 and '초과 치유' in at('AT_011','2023-04-05')['text']
assert at('AT_092','2017-04-04')['races']==[] and at('AT_092','2017-04-05')['races']==['ELEMENTAL']
assert at('AT_103','2018-07-10')['races']==[] and at('AT_103','2018-07-11')['races']==['BEAST']
assert at('AT_123','2022-11-29')['races']==['DRAGON'] and at('AT_123','2022-11-30')['races']==['DRAGON','UNDEAD']
for cid in ['AT_047','AT_094']:
 assert at(cid,'2024-10-29')['races']==[] and at(cid,'2024-10-30')['races']==['DRAENEI']
for cid,d in [('AT_001','2015-08-25'),('AT_063t','2015-08-25'),('OG_044c','2016-04-27'),('HERO_11bp2','2022-12-07'),('HERO_11bp2t','2022-12-07')]:
 assert at(cid,(date.fromisoformat(d)-timedelta(days=1)).isoformat()) is None and at(cid,d) is not None
bug=load('tools/tgt-known-unmodeled-intervals.json')['intervals'][0]
assert bug['id']=='AT_037' and bug['startDate']=='2020-03-27' and bug['restoredDate'] is None
assert [o[7] for o in obs['AT_037'] if o[0] in ['17.0.0.44222','17.0.0.44582']]==[4,1]
assert all('rarity' not in p['changes'] for p in docs['AT_037']['card']['patches'])
missing=load('tools/tgt-missing-ids.json')['cards'][0]
assert missing['id']=='AT_132_SHAMANe' and missing['dbfId']==72268 and missing['id'] not in docs
assert len(missing['observations'])==2 and all(o['nativeNumericObservations']['183']==15 for o in missing['observations'])
assert list(aggregate['events'])==sorted(aggregate['events'])
assert len(aggregate['events']['2015-08-25'])==149
assert sum(not c['initialDisplayMatchesRelease'] for c in audit['cards'])==manifest['partialInitialDisplayCardCount']
assert manifest['patchEvents']==sum(len(d['card']['patches']) for d in docs.values())
display(aggregate['events'])
print(json.dumps({'cards':152,'collectible':132,'tokensAndOptions':20,'datedEvents':manifest['patchEvents'],'forwardReverseAggregateBoundaryChecks':checks,'clientBuilds':manifest['selectedClientBuilds'],'clientNumericObservations':sum(map(len,obs.values())),'partialInitialDisplays':manifest['partialInitialDisplayCardCount'],'currentGameplaySpecChanges':0,'rawEvidencePreserved':True,'oldDateFirstPreserved':True,'supplementalReconstructionOnly':True}))
