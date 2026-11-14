#!/usr/bin/env python3
"""Narrow two-ID correction, honest confidence and opt-in absence semantics."""
import copy,json,subprocess,types,tempfile,shutil,sys
from pathlib import Path
from date_schema import *
from build_date_api import compile_history
ROOT=Path(__file__).resolve().parents[1]
BASE='d5e4954c86c658ff5adc0893add2ed1407c767ac'
IDS={'HERO_11bp2':79943,'HERO_11bp2t':87918}
DAYS=['1900-01-01','2022-11-29','2022-11-30','2022-12-01','2022-12-06','2022-12-07','2022-12-08','2099-12-31']
def old(path):return json.loads(subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT))
def old_bytes(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def index(x):return {c['id']:c for c in x['cards']}
def precise(record,day):
 if record.get('releaseBeforeDate') not in (None,'unavailable'):raise ValueError('Unknown wire policy')
 if day<record['releasedAt'] and (record['releaseStatus']=='verified' or record.get('releaseBeforeDate')=='unavailable'):return None
 state=copy.deepcopy(record['current']);state.pop('art',None)
 for row in record['history']:
  if row.get('from','0001-01-01')<=day<row.get('before','9999-12-31'):state=apply(state,row['changes'])
 return state

def main():
 evidence=load(ROOT/'tools/tgt-dk-availability-evidence.json')
 entries={c['id']:c for c in evidence['archive']['entries']}
 assert entries['HERO_11bp']['tags']['1086']=='79943' and entries['HERO_11cbp']['tags']['1086']=='99219'
 assert entries['HERO_11bp2']['englishText']==entries['HERO_11cbp2']['englishText']
 assert entries['HERO_11bp2t']['tags']['47']=='2' and entries['HERO_11bp2t']['tags']['45']=='1'
 assert evidence['releaseStatus']=='estimated'
 # Run prior resolver code independently; the original global default must stay unchanged.
 previous=types.ModuleType('previous_date_schema');previous.__file__=str(ROOT/'tools/date_schema.py');exec(old_bytes('tools/date_schema.py'),previous.__dict__)
 current=index(load(ROOT/'cards.json'));prior=index(old('cards.json'));history=load(ROOT/'history-date.json')['cards'];unchanged=0;cases=0
 for cid,c in current.items():
  timeline,meta=read_card(ROOT,cid);prior_t=old('data/'+cid+'.json');prior_m=old('metadata/'+cid+'.json')
  if cid not in IDS:
   reviewed=(cid=='AT_036' or meta.get('historicalTextCorrection',{}).get('dateConfidence')=='estimated-card-specific')
   if not reviewed:
    assert (ROOT/'data'/f'{cid}.json').read_bytes()==old_bytes('data/'+cid+'.json')
    assert (ROOT/'metadata'/f'{cid}.json').read_bytes()==old_bytes('metadata/'+cid+'.json')
   else:
    # The TGT full-set historical Korean text review deliberately changed
    # only earlier displayed wording. The archived source remains immutable.
    assert meta['originalSource']==prior_m['originalSource'],cid
    assert meta['currentCatalog']==prior_m['currentCatalog'],cid
    assert meta['release']==prior_m['release'],cid
   if reviewed:
    old_current=prior[cid]
    assert {k:v for k,v in c.items() if k!='text'}=={k:v for k,v in old_current.items() if k!='text'},cid
    assert c.get('text','').replace('_','')==old_current.get('text','').replace('_',''),(cid,'only approved display underscore may differ')
   else:
    assert c==prior[cid],cid
   for day in DAYS:
    present=resolve(timeline,meta,day);before=previous.resolve(prior_t,prior_m,day)
    if reviewed:
     assert present is not None and before is not None or present==before,cid
     if present is not None and before is not None:
      assert {k:v for k,v in present.items() if k!='text'}=={k:v for k,v in before.items() if k!='text'},(cid,day)
      assert present.get('text','').replace('_','')==before.get('text','').replace('_',''),(cid,day,'modern display text drift')
    else:
     assert json_equal(present,before),(cid,day)
    unchanged+=1
   continue
  assert c['dbfId']==IDS[cid]
  expected=copy.deepcopy(prior[cid]);expected.update(releasedAt='2022-11-30',releaseStatus='estimated');assert c==expected
  assert meta['release']=={'date':'2022-11-30','status':'estimated','beforeDate':'unavailable'}
  assert list(timeline)==['2022-11-30'] and list(prior_t)==['2022-12-07']
  assert timeline['2022-11-30']==prior_t['2022-12-07']
  for key in ('originalSource','currentCatalog','supplementalAudit','sourceCommit'):assert meta[key]==prior_m[key],key
  for day in DAYS:
   expected=None if day<'2022-11-30' else fold(timeline)
   assert json_equal(resolve(timeline,meta,day),expected)
   assert json_equal(precise(history[str(c['dbfId'])],day),expected);cases+=1
   # Old PHP ignores release metadata, has no history rows for these IDs and
   # continues returning its old current-card fallback on both sides of date.
   assert str(c['dbfId']) not in load(ROOT/'history.json')['cards']
   assert {k:v for k,v in c.items() if k not in ('releasedAt','releaseStatus')}=={k:v for k,v in prior[cid].items() if k not in ('releasedAt','releaseStatus')}
  removed=copy.deepcopy(meta);removed['release'].pop('beforeDate')
  assert resolve(timeline,removed,'1900-01-01')==fold(timeline),'Legacy estimated default changed'
  for bad in ('visible','unknown',None,False,0,[]):
   invalid=copy.deepcopy(meta);invalid['release']['beforeDate']=bad
   try:resolve(timeline,invalid)
   except ValueError:pass
   else:raise AssertionError('Unknown policy accepted')
  mismatched=copy.deepcopy(meta);mismatched['release']['date']='2022-12-07'
  try:resolve(timeline,mismatched)
  except ValueError:pass
  else:raise AssertionError('Policy date differs from canonical baseline')
  try:resolve(timeline,meta,'2022-12-07',strict=True)
  except UncertainHistory:pass
  else:raise AssertionError('Estimated timing promoted to strict verification')
  extended=copy.deepcopy(timeline);extended['2090-01-01']={'cost':0}
  assert compile_history(extended,meta)[0]['from']=='2022-11-30'
  assert 'from' not in compile_history(extended,removed)[0]
 for filename in ('cards-date.json','render-date.json','history-date.json'):
  bundle=load(ROOT/filename);records=bundle['cards'].values() if isinstance(bundle['cards'],dict) else bundle['cards']
  assert {c['id'] for c in records if 'releaseBeforeDate' in c}==set(IDS)
 for filename in ('cards.json','render.json','history.json'):assert 'releaseBeforeDate' not in (ROOT/filename).read_text()
 archived_history=old('history.json')
 for dbf in ('16221','16222','16223','16225'):archived_history['cards'].pop(dbf,None)
 active=load(ROOT/'history.json')['cards']
 for cid,c in current.items():
  if cid in IDS:continue
  dbf=str(c['dbfId'])
  if cid=='AT_036' or load(ROOT/'metadata'/f'{cid}.json').get('historicalTextCorrection'):
   assert (dbf in active) or cid=='AT_036',(cid,'expected corrected historical interval')
  else:
   assert active.get(dbf)==archived_history['cards'].get(dbf),(cid,'unexpected unrelated legacy history')
 assert not set(active).intersection({'16221','16222','16223','16225'})
 assert (ROOT/'data/history.json').read_bytes()==old_bytes('data/history.json')
 # Invalid policy is rejected by the real builder, not just a helper test.
 with tempfile.TemporaryDirectory(prefix='tgt-dk-invalid-',dir='/tmp') as tmp:
  sandbox=Path(tmp)
  for name in ('tools','data','metadata'):shutil.copytree(ROOT/name,sandbox/name)
  shutil.copy2(ROOT/'cards.json',sandbox/'cards.json')
  invalid=load(sandbox/'metadata/HERO_11bp2.json');invalid['release']['beforeDate']='unknown'
  put(sandbox/'metadata/HERO_11bp2.json',invalid)
  result=subprocess.run([sys.executable,str(sandbox/'tools/build-api.py')],capture_output=True,text=True)
  assert result.returncode and 'Unknown release.beforeDate policy' in result.stderr
 report={'result':'pass','baseCommit':BASE,'correctedIDs':IDS,'estimatedKoreanDate':'2022-11-30','classUnlock':'2022-12-07','targetDateCases':cases,'unchangedOtherCardDateCases':unchanged,'immutableSourceSnapshots':'preserved','unknownPolicies':'rejected by resolver and real builder','strictEstimatedLookup':'rejected','oldPhpFallback':'unchanged; no before-date absence support','precisePolicy':'releaseBeforeDate=unavailable on exactly two IDs across all three precise siblings'}
 put(ROOT/'tools/tgt-dk-availability-validation.json',report);print(json.dumps(report))
if __name__=='__main__':main()
