"""Explicit lossy schema-1 boundary for the unchanged installed plugin.

Never write this projection back to canonical data or confidence sidecars.
"""
from __future__ import annotations
import copy
from date_schema import SPECS, apply, json_equal, resolve

LEGACY_FIELDS = ("name", "type", "cardClass", "classes", "rarity", "collectible",
                 "cost", "attack", "health", "durability", "armor", "text",
                 "races", "race", "spellSchool", "mechanics", "legacyArt")
RENDER_FIELDS = ("id", "dbfId", "name", "type", "cardClass", "rarity", "collectible",
                 "cost", "text", "attack", "health", "durability", "armor", "art",
                 "races", "race", "spellSchool", "set", "nativeTags", "mechanics",
                 "watermark", "classes", "releasedAt", "releaseStatus")
PHP_FIELDS = ("name", "cost", "text", "attack", "health", "durability", "armor",
              "race", "spellSchool", "art", "legacyArt", "type", "cardClass",
              "rarity", "watermark", "mechanics", "nativeTags")


def project_legacy(state, meta):
    """Represent exact state using documented old wire sentinels only."""
    original = meta['currentCatalog']
    managed = set(meta.get('canonicalFields', [])) | set(original)
    result = {k:copy.deepcopy(v) for k,v in state.items() if k in LEGACY_FIELDS}
    for key in ('cost','attack','health','durability','armor'):
        if key not in result:
            # The old renderer/exporter used health as the weapon's mirror.
            # Preserve that legacy representation only at this output boundary.
            if key == 'health' and state.get('type') == 'WEAPON':
                result[key] = state.get('durability',0)
            else:
                result[key] = 0
    for key,empty in (('text',''),('race',''),('races',[]),('spellSchool',''),('mechanics',[]),('classes',[])):
        if key not in result and (key == 'text' or key in managed):
            result[key] = copy.deepcopy(empty)
    # Preserve the pinned endpoint's annotation convention, not a frozen card.
    # Implementation markers and referenced-keyword annotations remain confined
    # to schema1. Future canonical keyword changes still flow through.
    convention = meta['legacyMechanicsConvention']
    owned = state.get('mechanics', [])
    baseline = convention['canonicalBaseline']
    previous = convention['original']
    legacy = [m for m in previous if m not in baseline or m in owned]
    legacy += [m for m in owned if m not in baseline and m not in legacy]
    if convention['present'] or legacy:
        result['mechanics'] = legacy
    else:
        result.pop('mechanics', None)
    # Old JSON always has these required common fields in this TGT corpus.
    # Do not invent unsupported data for a different expansion silently.
    for field in ('name','type','cardClass','rarity','collectible'):
        if field not in result:
            raise ValueError(f"Schema-1 compatibility cannot supply missing {field}: {state.get('id')}")
    return result


def compile_legacy(timeline, meta, precise_record):
    record = copy.deepcopy(meta['currentCatalog'])
    record.pop('history', None)
    latest = resolve(timeline,meta)
    current = project_legacy(latest,meta)
    for field in LEGACY_FIELDS:
        if field == 'legacyArt':
            continue  # old current catalogue never advertised this flag
        if field in current:
            if field in ('race','races') and field not in record and not current[field]:
                continue
            record[field] = copy.deepcopy(current[field])
    record['releasedAt'] = meta['release']['date']
    record['releaseStatus'] = meta['release']['status']
    if timeline:
        points=list(timeline.items())
        start,state=points[0]
        events=[{'date':d,'changes':c} for d,c in points[1:]]
    else:
        start=None
        state=copy.deepcopy(meta['undated']['baseline'])
        events=meta['undated']['patches']
    revisions=[]
    for event in events:
        old=project_legacy(state,meta)
        changes={k:copy.deepcopy(v) for k,v in old.items()
                 if k not in current or not json_equal(v,current[k])}
        # Every old field is representable or normalized to the legacy
        # sentinel. No __remove operation reaches an old parser.
        if changes:
            revision={'before':event['date'],'changes':changes}
            if start:revision['from']=start
            revisions.append(revision)
        state=apply(state,event['changes'])
        start=event['date']
    return record,revisions


def loss_report():
    return {
        'schema':1,'scope':'Only old schema1 endpoints; canonical and -date endpoints retain exact presence.',
        'legacyConsumer':'qxwd565/HSdeck-plugin 78ce6fdc4e70f689880a70d6f22aa77a6c75e337 (unmodified)',
        'rules':[
            'Absent combat stats retain zero sentinels only at the old output boundary. Five weapon records preserve the original health/durability mirror.',
            'Original endpoint field presence is preserved; precise intrinsic mechanics are separate from old annotation conventions.',
            '54 current texts normalize raw newline syntax to <br></br>;152 records gain independently sourced release metadata. No other current catalog changes.',
            'History previously empty is now schema1 reverse history equal to the separately retained unpublished104-event audit.',
            'Before-release old-parser fallback remains unchanged. No strict/default visibility gate is enabled.',
            'Current native tags, relationships, IDs, DBFs and artwork are unchanged. Canonical future edits still propagate through this narrow compatibility projection.',
        ],
        'limitations':[
            'Old numeric sentinel conventions cannot distinguish absent stats from zero or implement general removal.',
            'Old PHP whitelist omits races/classes/collectible and arbitrary effect fields; installed current native tags can leak into historical rendering.',
            'Two hero powers remain unsupported old renderer frame types. No live site/import/database/plugin changes or live UI proof.',
            'Current immutable source preserves raw evidence. Historical initial display, early rarity/class boundaries and Living Roots restoration remain partially unresolved.',
        ],
        'preciseEndpoints':{'cards':'cards-date.json','render':'render-date.json','history':'history-date.json'},
        'artRule':'All six bundles remain root siblings, retaining art/<ID> URL bases.',
    }
