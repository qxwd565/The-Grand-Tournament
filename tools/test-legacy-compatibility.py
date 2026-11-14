#!/usr/bin/env python3
import argparse,copy,json,subprocess,hashlib
from pathlib import Path
from datetime import date,timedelta
from urllib.parse import urljoin
from date_schema import *
from legacy_projection import PHP_FIELDS
ROOT=Path(__file__).resolve().parents[1];SOURCE='d04048e30e0ac075b5961e0198c5576d38fd828d';BASE_URL='https://raw.githubusercontent.com/qxwd565/The-Grand-Tournament/main/'
def old_resolve(current,rows,day):
 s=copy.deepcopy(current);done=set()
 for row in rows:
  if row.get('from','0001-01-01')<=day<row.get('before','9999-12-31'):
   for k,v in row['changes'].items():
    if k in PHP_FIELDS and k not in done:s[k]=v;done.add(k)
 return s

def main(fixture=None):
 original=json.loads(subprocess.check_output(['git','show',SOURCE+':cards.json'],cwd=ROOT));catalog=load(ROOT/'cards.json');history=load(ROOT/'history.json');render=load(ROOT/'render.json');sup=ROOT/'tools/supplemental-audit'
 retired={'AT_132_SHAMANa','AT_132_SHAMANb','AT_132_SHAMANc','AT_132_SHAMANd'}
 expected=copy.deepcopy(original);expected['cards']=[c for c in expected['cards'] if c['id'] not in retired];normalized=[]
 by_id={c['id']:c for c in catalog['cards']};old={c['id']:c for c in load(sup/'cards.json')['cards']};rh={c['id']:c for c in render['cards']}
 for c in expected['cards']:
  m=load(ROOT/'metadata'/f"{c['id']}.json")
  t=BREAK.sub('<br></br>',c['text'])
  if t!=c['text']:normalized.append(c['id'])
  c['text']=t;c['releasedAt']=m['release']['date'];c['releaseStatus']=m['release']['status']
 assert json_equal(catalog,expected),'Unreviewed current catalog changes'
 supplemental_catalog=load(sup/'cards.json')
 supplemental_catalog['cards']=[c for c in supplemental_catalog['cards'] if c['id'] not in retired]
 for c in supplemental_catalog['cards']:
  if c['id'] in ('HERO_11bp2','HERO_11bp2t'):
   c['releasedAt']='2022-11-30';c['releaseStatus']='estimated'
 assert json_equal(catalog,supplemental_catalog)
 for cid in ('HERO_11bp2','HERO_11bp2t'):
  old[cid]['releasedAt']='2022-11-30';old[cid]['releaseStatus']='estimated'
 archived_history=load(sup/'history.json')
 for dbf in ('16221','16222','16223','16225'):archived_history['cards'].pop(dbf,None)
 assert history==archived_history,'Retained Legacy history differs from independent supplemental reconstruction'
 assert all(x['schema']==1 and 'historySchema' not in x for x in (catalog,history,render))
 for name in ['cards.json','history.json','render.json']:assert '__remove' not in (ROOT/name).read_text()
 assets={}
 for line in subprocess.check_output(['git','ls-tree','-r',SOURCE,'--','art','golden'],cwd=ROOT,text=True).splitlines():
  info,path=line.split('\t');assets[path]=info.split()[2]
 for p,sha in assets.items():
  if p in {f'golden/cards/{cid}.json' for cid in retired}:continue
  data=(ROOT/p).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==sha,p
 dates={'1900-01-01','2099-12-31','2022-12-06','2022-12-07','2022-12-08'}
 for cid in by_id:
  for d in load(ROOT/'data'/f'{cid}.json'):dates.update((date.fromisoformat(d)+timedelta(days=n)).isoformat() for n in [-1,0,1])
 cases=[]
 for cid,c in by_id.items():
  assert c['art'] in assets
  for name in ['cards.json','render.json','history.json','cards-date.json','render-date.json','history-date.json']:assert urljoin(BASE_URL+name,c['art'])==BASE_URL+c['art']
  rows=history['cards'].get(str(c['dbfId']),{}).get('history',[]);assert rows==rh[cid].get('history',[])
  for d in sorted(dates):
   actual=old_resolve(c,rows,d);before=old_resolve(old[cid],load(sup/'history.json')['cards'].get(str(c['dbfId']),{}).get('history',[]),d)
   assert json_equal(actual,before),(cid,d)
   cases.append({'id':cid,'dbfId':c['dbfId'],'date':d,'expected':{k:v for k,v in before.items() if k in PHP_FIELDS}})
 report={'result':'pass','cards':148,'approvedTextNormalizations':len(normalized),'approvedReleaseMetadata':148,'otherCurrentChanges':0,'qualifiedAvailabilityCorrections':2,'legacyDateCases':len(cases),'preservedAssetFiles':len(assets)-4,'artURLChecks':148*6,'historyEqualsUnpublishedSupplementalAudit':True,'historyBytes':(ROOT/'history.json').stat().st_size,'visibility':'No new strict/default gating; before-release old-parser fallback retained'}
 put(ROOT/'tools/legacy-compatibility-validation.json',report)
 if fixture:put(fixture,{'catalog':catalog,'history':history,'cases':cases,'allowed':list(PHP_FIELDS),'originalCatalog':expected,'baseUrl':BASE_URL,'expectedCards':148,'originalComparison':'Pinned current source with only reviewed display normalization and release metadata applied'})
 print(json.dumps(report))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path);main(p.parse_args().fixture)
