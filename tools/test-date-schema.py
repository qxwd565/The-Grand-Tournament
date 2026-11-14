#!/usr/bin/env python3
import copy,json,subprocess,hashlib
from pathlib import Path
from datetime import date,timedelta
from collections import Counter
from date_schema import *
ROOT=Path(__file__).resolve().parents[1];SOURCE='d04048e30e0ac075b5961e0198c5576d38fd828d'
def require_source_commit(root,commit):
 if subprocess.run(['git','cat-file','-e',commit+':data'],cwd=root,capture_output=True).returncode:raise RuntimeError('Pinned source unavailable; use checkout fetch-depth: 0')
def original(p):return json.loads(subprocess.check_output(['git','show',SOURCE+':'+p],cwd=ROOT))
def reverse(record,day):
 if day<record['releasedAt']:return None
 s=copy.deepcopy(record['current']);s.pop('art',None)
 matches=[e for e in record['history'] if e.get('from','0001-01-01')<=day<e.get('before','9999-12-31')];assert len(matches)<=1
 for e in matches:
  for k in e['changes'].get('__remove',[]):s.pop(k,None)
  s.update({k:v for k,v in e['changes'].items() if k!='__remove'})
 return s

def main():
 require_source_commit(ROOT,SOURCE);current={c['id']:c for c in original('cards.json')['cards'] if c['id'] not in {'AT_132_SHAMANa','AT_132_SHAMANb','AT_132_SHAMANc','AT_132_SHAMANd'}};precise={c['id']:c for c in load(ROOT/'cards-date.json')['cards']};h=load(ROOT/'history-date.json');assert h['historySchema']==2
 assert set(current)==set(precise)=={p.stem for p in (ROOT/'metadata').glob('*.json')} and len(current)==148
 dates={'1900-01-01','2099-12-31','2022-12-06','2022-12-07','2022-12-08'};maps={};metas={};events=0
 for cid in current:
  t,m=read_card(ROOT,cid);maps[cid]=t;metas[cid]=m;validate_timeline(t)
  assert m['originalSource']==original('data/'+cid+'.json')
  assert m['currentCatalog']==current[cid] and m['sourceCommit']==SOURCE
  doc=load(ROOT/'tools/supplemental-audit'/f'{cid}.json');assert m['supplementalAudit']['document']==doc and m['supplementalAudit']['status']=='unpublished-reconstruction'
  expected=projected_states(doc)
  for d,s in expected:assert json_equal(fold(t,d),s),(cid,d)
  assert json_equal(fold(t),{k:precise[cid][k] for k in m['canonicalFields'] if k in precise[cid]})
  events+=len(t)-1
  for d in t:
   dates.update((date.fromisoformat(d)+timedelta(days=n)).isoformat() for n in (-1,0,1))
  try:resolve(t,m,'2015-08-25',strict=True)
  except UncertainHistory:pass
  else:raise AssertionError('Partial baseline silently verified')
 cases=0
 for cid,t in maps.items():
  for d in sorted(dates):assert json_equal(fold(t,d),reverse(h['cards'][str(current[cid]['dbfId'])],d)),(cid,d);cases+=1
 # Preserved original date-first aggregate is evidence, not another writable canonical source.
 assert load(ROOT/'data/history.json')==original('data/history.json')
 assert fold(maps['AT_063t'])['collectible'] is True
 assert 'attack' not in fold(maps['HERO_11bp2']) and fold(maps['HERO_11bp2'])['rarity'] is None
 assert fold(maps['AT_042a'],'2018-11-29')['type']=='SPELL' and 'attack' not in fold(maps['AT_042a'],'2018-11-29')
 assert fold(maps['AT_042a'],'2018-11-30')['attack']==2
 assert fold(maps['AT_024'],'2015-09-29')['race']=='악마' and 'race' not in fold(maps['AT_024'],'2015-09-30')
 assert '__remove' in maps['AT_024']['2015-09-30']
 assert fold(maps['AT_012'],'2023-09-06')['health']==4 and fold(maps['AT_012'],'2023-09-07')['health']==5
 report={'result':'pass','cards':148,'preciseGlobalDateCases':cases,'dates':len(dates),'sparseEvents':events,'preservedSupplementalEvents':100,'originalSourceDocuments':148,'partiallyVerifiedBaselines':148,'currentTypes':dict(Counter(fold(t)['type'] for t in maps.values()))}
 put(ROOT/'tools/date-schema-validation.json',report);print(json.dumps(report))
if __name__=='__main__':main()
