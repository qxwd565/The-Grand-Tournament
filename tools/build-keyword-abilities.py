from pathlib import Path
import json,copy
r=Path(__file__).resolve().parents[1];e=json.load(open(r/'tools/tgt-mechanics-evidence.json'))
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
base={};events={}
for p in sorted((r/'tools/supplemental-audit').glob('*.json')):
 doc=json.load(open(p))
 if 'card' not in doc:continue
 c=copy.deepcopy(doc['card']);cid=c['id'];initial=next(b['cards'][cid] for b in e['builds'] if cid in b['cards'])
 owned=[x for x in initial['actualMechanics'] if x not in ['AURA','TRIGGER_VISUAL','CASTS_WHEN_DRAWN']]
 if cid in ['AT_004','AT_005','HERO_11bp2']:owned=[]
 def state_abilities(c):
  a=owned.copy();t=c.get('text','')
  if '격려' in t:a.append('INSPIRE')
  if cid in ['AT_037','AT_042']:a.append('CHOOSE_ONE')
  if cid in ['AT_012','AT_018','AT_049'] and '전투의 함성' in t:a.append('BATTLECRY')
  if cid=='AT_036t' and '죽음의 메아리' in t:a.append('DEATHRATTLE')
  if cid=='AT_006' and t.startswith('<b>주문 공격력'):a.append('SPELLPOWER')
  if cid=='AT_011' and '초과 치유' in t:a.append('OVERHEAL')
  if cid=='AT_035t' and '뽑을 때 시전' in t:a.append('CASTS_WHEN_DRAWN')
  if cid in ['AT_042a','AT_042b'] and c['type']=='MINION':a.append('CHARGE' if cid.endswith('a') else 'STEALTH')
  if cid=='OG_044c':a=['CHARGE','STEALTH']
  return sorted(set(a))
 base[cid]=prior=state_abilities(c)
 for event in c.get('patches',[]):
  c.update(event['changes']);a=state_abilities(c)
  if a!=prior:events.setdefault(cid,{})[event['date']]=a;prior=a
put(r/'tools/tgt-keyword-abilities.json',{'schema':1,'vocabulary':sorted(set(e['mechanicTags'].values())-{'AURA','TRIGGER_VISUAL'}|{'OVERHEAL'}),'scope':'Bounded intrinsic keyword vocabulary, not every free-text effect. Joust comparisons, conditional keyword grants, hero-power improvements and amount-bearing effects remain in text. Implementation/reference tags are separately preserved.','baseline':base,'events':events,'semanticExceptions':{'AT_004':'Benefits from Spell Damage; does not supply Spell Damage.','AT_005':'References transformed token Charge; token AT_005t owns it.','HERO_11bp2':'Summons Charge ghoul; power does not own Charge.','AT_006':'Gains own Spell Damage on2023-08-23 despite missing actual tag.','AT_035t':'Historical automatic draw effect predates formal Casts When Drawn text; list acquires displayed keyword with2018-10-03 text.','AT_130':'Minion with a draw trigger, not a Casts When Drawn spell. Later implementation flag is excluded.','AT_042a/b':'Choice spells describe output form; own keywords begin with2018-11-30 MINION previews.','AT_037/042':'Choose One in release text before dedicated tag443.','AT_051/069/132':'Temporary missing engine tags do not remove unchanged own text keywords.'}})
