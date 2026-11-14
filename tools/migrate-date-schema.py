#!/usr/bin/env python3
"""Pinned published originals plus explicitly unpublished audited reconstruction."""
import copy,json,subprocess
from pathlib import Path
from date_schema import *
ROOT=Path(__file__).resolve().parents[1]
SOURCE='d04048e30e0ac075b5961e0198c5576d38fd828d'
RETIRED_CHOICES = frozenset(('AT_132_SHAMANa', 'AT_132_SHAMANb', 'AT_132_SHAMANc', 'AT_132_SHAMANd'))

def retire_redundant_choice_entries():
 # A pinned old archive includes four separate Totemic Slam choices.
 # They must not be resurrected in a clean rebuild. Basic summonable totems
 # and the empowered Shaman hero power are not altered by this migration.
 catalog = load(ROOT/'cards.json')
 rows = [card for card in catalog['cards'] if card['id'] not in RETIRED_CHOICES]
 if len(rows) != len(catalog['cards']):
  catalog['cards'] = rows
  put(ROOT/'cards.json', catalog)
 for cid in RETIRED_CHOICES:
  for directory in ('data', 'metadata', 'golden/cards', 'tools/supplemental-audit'):
   (ROOT/directory/f'{cid}.json').unlink(missing_ok=True)

def main():
 retire_redundant_choice_entries()
 try:original_catalog=json.loads(subprocess.check_output(['git','show',SOURCE+':cards.json'],cwd=ROOT))
 except subprocess.CalledProcessError:raise RuntimeError('Pinned source missing; require checkout fetch-depth: 0')
 current={c['id']:c for c in original_catalog['cards'] if c['id'] not in RETIRED_CHOICES};audit=load(ROOT/'tools/tgt-release-audit.json');evidence=load(ROOT/'tools/tgt-mechanics-evidence.json');changed=0
 for cid in sorted(current):
  path=ROOT/'data'/f'{cid}.json';doc=load(path)
  if 'card' not in doc:
   validate_timeline(doc);assert (ROOT/'metadata'/path.name).exists();continue
  original=json.loads(subprocess.check_output(['git','show',SOURCE+':data/'+path.name],cwd=ROOT));assert doc==original
  assert not (ROOT/'metadata'/path.name).exists()
  supplemental=load(ROOT/'tools/supplemental-audit'/path.name)
  timeline,meta=migrate_document(supplemental,current[cid],SOURCE)
  meta['originalSource']=original
  meta['legacyMechanicsConvention']={'present':'mechanics' in current[cid], 'original':current[cid].get('mechanics',[]),'canonicalBaseline':fold(timeline)['mechanics']}
  meta['supplementalAudit']={'status':'unpublished-reconstruction','source':'tools/supplemental-audit/'+path.name,'document':supplemental,'meaning':'Preserved vetted audit, never published under sourceCommit. Source-backed reconstruction supplies initial and later specs, while originalSource is the actual published original.'}
  meta['currentOnlyFields']=sorted(set(current[cid])-set(meta['canonicalFields'])-{'releasedAt','releaseStatus'})
  meta['availabilityScope']='Korean ordinary constructed-match use; excludes preview, preload and early adventure use. No new default visibility gate.'
  meta['dateRecheckEvidence']='tools/tgt-date-recheck.json'
  meta['confidenceNote']='Partial baseline verification. Initial Korean display timelines and generated-card rarity/class boundaries remain qualified. Client tags alone do not establish Korean server-live effective dates.'
  meta['undatedEvidence']={'historicalTextObservations':supplemental.get('historicalTextObservations',[]),'knownUnmodeledIntervals':'tools/tgt-known-unmodeled-intervals.json','missingIDs':'tools/tgt-missing-ids.json'}
  meta['abilityImplementationObservations']=[];prior=None
  for b in evidence['builds']:
   if cid not in b['cards']:continue
   c=b['cards'][cid];v={kind:{tag:value for tag,value in c[kind].items() if tag in evidence['mechanicTags']} for kind in ('Tag','ReferencedTag')}
   if prior!=v:meta['abilityImplementationObservations'].append({'build':b['build'],'source':b['source'],**v,'dateStatus':'Observation only; not an asserted Korean gameplay change'});prior=v
   else:meta['abilityImplementationObservations'][-1]['lastObservedBuild']=b['build']
  if cid in ['AT_037','AT_037a','AT_037b','AT_037t','AT_042a','AT_042b']:
   meta['fieldUncertainty']={'rarityAndClass':{'status':'partial','meaning':'Preserved provisional display values; archive tags may describe implementation changes. No invented live restoration or early generated-option boundary.','source':'tools/tgt-known-unmodeled-intervals.json'}}
  if original['card'].get('rarity', 'ABSENT') is None:meta['rarityPresenceEvidence']={'status':'unknown','value':None,'meaning':'Explicit null from source is preserved as unknown; not a fabricated absence or default rarity.'}
  if cid.startswith('HERO_'):meta['heroEvidence']={'role':'base-class-hero-entity','meaning':'Not a playable replacement hero card. Source-backed health is retained; no inferred armor or unrelated combat stats.'}
  put(ROOT/'metadata'/path.name,meta);put(path,timeline);changed+=1
 from availability_correction import apply_correction
 apply_correction(ROOT)
 print(json.dumps({'migrated':changed,'sourceCommit':SOURCE}))
if __name__=='__main__':main()
