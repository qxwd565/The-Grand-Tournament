# Date-first The Grand Tournament API

Scope: all 152 existing card IDs in qxwd565/The-Grand-Tournament, pinned original main d04048e30e0ac075b5961e0198c5576d38fd828d. Includes 132 collectible cards and 20 other records. AT_063t is collectible despite its suffix. Current precise types: 114 MINION, 31 SPELL, 5 WEAPON, 2 HERO_POWER. No other expansion, plugin, site, database, cache or source configuration is changed.

## Source and reconstruction provenance

The original card files were schemaVersion 1 current-only wrappers. Original cards.json and render.json were schema 1 current catalogs; original history.json was schema 1 with an empty cards object. They were not published versions of the earlier 104-event audit.

metadata/<ID>.json preserves the actual pinned originalSource and currentCatalog, including raw text, native tags, assets and relationships. tools/supplemental-audit contains the explicitly unpublished audited reconstruction and its own evidence. It is not falsely labeled as the source commit. The migration reads actual originals from Git plus committed supplemental inputs. A clean pinned-source checkout regenerates all 311 canonical/sidecar/bundle files exactly.

The original data/history.json is a legacy date-first aggregate, not a card-ID file. It is retained byte-for-byte as noncanonical evidence and is excluded from card iteration. Its stale values must not be used as the authoritative timeline. The canonical 152 files are selected by catalog IDs. The copied tools/original-date-first-history.json likewise is evidence only. No old pending work or uploads are resumed or overwritten.

## Canonical state and presence

Each data/<CARD_ID>.json has ascending KST dates, known full initial specs, then sparse changes. 104 existing audited events remain, now including 9 justified keyword changes within those existing dates. Missing fields inherit. __remove explicitly deletes an attribute. Zero, false, null, empty strings/lists and absence remain distinct. Unknown rarity null stays explicit unknown, not invented absence. Spells and powers receive no fake combat stats; weapons use durability, not health. Druid choices become MINION previews on 2018-11-30 and acquire corresponding stats. Demonfuse's historical Demon affiliation is explicitly removed on 2015-09-30. Display text uses exactly <br></br>; original raw evidence remains verbatim.

Current-only native/portrait/flavor/set metadata is not backdated. All 152 baselines remain partially verified; 58 initial Korean display timelines and early Druid rarity/class boundaries remain unresolved. Strict historical resolution rejects partial baselines. Old schema1 consumers retain their existing behavior; no new global hiding or strict gate is enabled. The two Death Knight records explicitly preserve precise before-date absence even though their corrected date is estimated; see the availability follow-up below.

## Dates and limitations

First use follows Korean ordinary constructed matches. 149 records start 2015-08-25; Fandral's combined form OG_044c begins 2016-04-27; upgraded Death Knight power HERO_11bp2 and ghoul HERO_11bp2t now use an estimated 2022-11-30 first-generation date. December 7 is confirmed class unlock, not earliest generated use. Contemporary generation reports provide evidence beyond client preload; the exact original-ID match binding and Korean first-use day remain inferred. Demon Hunter April 8 is a class-unlock date only, not an audit of earliest generated availability. Reports of ordinary Wild generation on March 27 predate that unlock ([HearthPwn](https://www.hearthpwn.com/forums/hearthstone-general/general-discussion/241225-hero-power-for-demon-hunter-available), [Reddit](https://www.reddit.com/r/hearthstone/comments/fpfra7)). Demon Hunter records and any date correction are outside this two-card scope.

Draenei on AT_047/094 begins 2024-10-30 with 31.0, not expansion unlock. AT_012 changes cost/text on 2023-08-23 but its health only on 2023-09-07 after the client-and-server fix. Aviana 2018-10-19 and Astral Communion 2026-04-03 retain qualified prior evidence, not newly claimed Korean completion proof. Living Roots' actual temporary rarity gem bug begins 2020-03-27, but the Korean restoration day is unresolved despite the restored client build. Canonical COMMON across that interval is an explicit known limitation; no guessed endpoint or open-ended EPIC patch is added. Missing AT_132_SHAMANe assets/provenance/first-use remain unresolved; no record or art is fabricated. See tools/tgt-date-recheck.json and preserved audit evidence.

## Intrinsic keywords and implementation flags

46 selected XML archives yield 6,931 observations, with actual Tag and ReferencedTag separated and full-file hashes/source URLs retained. The bounded intrinsic list is not every effect. Empty mechanics does not mean effectless. Joust comparisons, conditional grants, hero-power effects and amounts remain in full text.

Choose One is present in release text before tag 443. Inspire uses actual 403 and own text. AT_006 gains actual Spell Damage with its 2023 buff despite missing tag evidence; AT_012/018/049 gain Battlecry on that date. AT_011 gains Overheal on 2023-04-05. Druid option spells describe forms; intrinsic Charge/Stealth begin with their later MINION previews. AT_035t's automatic draw behavior predates its formal 2018 Casts When Drawn wording.

AT_004 benefits from Spell Damage but does not grant a Spell Damage aura. AT_005 and HERO_11bp2 reference the created minions' Charge. AT_130 Sea Reaver / 바다의 학살자 remains a minion with a draw trigger, not a Casts When Drawn spell. Missing/fluctuating flags on AT_051/069/132 do not create fictional gameplay changes. AURA/TRIGGER_VISUAL remain separate implementation evidence. Raw/current tags are untouched.

## Compatible and precise endpoints

All six endpoints are siblings, keeping existing art/<ID> URL bases.

- cards.json, render.json, history.json retain schema 1 for unchanged clients. The only current catalog changes are 54 newline normalizations plus release metadata on 152 records. Numbers, types, IDs, artwork and all other fields match pinned originals. New schema 1 history is exactly equal to the independently retained supplemental 104-event reconstruction, not to the formerly empty published history.
- cards-date.json, render-date.json, history-date.json expose precise current states and historySchema 2 with disjoint reverse intervals and explicit removals.

The old transport retains zero placeholders and weapon health/durability mirroring only at its boundary. It preserves original endpoint mechanics conventions without freezing future approved canonical cost/keyword changes. The unchanged PHP whitelist cannot express every field or absence and current native tags can leak into historical renderer state. Two hero-power frames remain a plugin limitation. Offline parser tests are not live site/rendering/import proof. Do not switch the postponed plugin to precise endpoints yet.

## Verification and rebuild

Run python3 tools/migrate-date-schema.py and python3 tools/build-api.py. CI uses the local committed builder and fetch-depth:0. The old writer is disabled; its read-only validation helpers remain in wrapper_api_reference.py.

Tests: test-tgt-history.py, test-presence-fixtures.py, test-date-schema.py, test-tgt-mechanics.py, test-legacy-compatibility.py, test-future-canonical.py, test-build-idempotence.py, test-clean-migration.py. Run each with python3, then git diff --check.

Coverage: 152 originals; 104 supplemental events; 1,680 independent audit boundaries; 12,616 global-date precise cases; 12,616 old-consumer cases; 6,931 numeric and 6,931 mechanic observations from the same 46 builds (overlapping evidence, not 13,862 independent snapshots). All 825 art/golden files and 912 sibling art URL checks remain intact. Typed fixtures include zero/false/null/empty/removal/type transitions. Clean regeneration matches 311 files, including retained data/history.json. Future canonical changes propagate and repeated builds are idempotent.

The exact unchanged PHP blobs from plugin 78ce6fdc4e70f689880a70d6f22aa77a6c75e337 were hash-verified. PHP WASM 8.5.12 passes 12,617 checks for 152 imports plus historical cases. See tools/unmodified-php-validation.json. No plugin source was edited.

## Death Knight generation availability follow-up

A narrow correction after the first migration moves only HERO_11bp2 / 79943 and HERO_11bp2t / 87918 from 2022-12-07 to an estimated 2022-11-30. The full initial gameplay state is unchanged. Original published source snapshots, currentCatalog and the previously unpublished audit documents remain immutable; tools/availability_correction.py applies a separate evidence-backed layer after migration. tools/tgt-dk-availability-evidence.json records sources and limitations.

The exact 25.0 archive maps base original power 78162 to upgraded original 79943 via tag 1086. Cosmetic Darion power 99218 separately maps to 99219 with identical names and text, so name matching alone does not prove the reported match ID. The original 2/1 Charge Undead token is 87918. Readable contemporary community comments describe pre-class-launch Finley/Yoink generation and the upgraded ghoul. The Korean official patch article explicitly places 25.0 on November 30 and class/prologue unlock on December 7. This is medium-high patch-derived availability confidence, not a Korean match timestamp, logged exact-ID observation or proof of a particular Finley-to-Justicar chain. Image evidence was not independently inspected; exact match IDs and regional timestamps remain unbound.

Metadata release.status is estimated, never relabeled verified to force a gate. The optional per-card release.beforeDate="unavailable" policy applies only to these two IDs. Canonical resolve returns no card before the adopted date, as fold already does, and strict lookup continues to reject estimated history. Omitted policy retains the previous estimated-date fallback for all other cards. Unknown policy values fail validation.

All three precise siblings expose the matching optional releaseBeforeDate="unavailable" field. Precise consumers must honor this field before resolving history, even when releaseStatus is estimated: a requested day earlier than releasedAt returns no card. Normal current lookups are unaffected. Precise history intervals also retain an explicit lower bound when that policy is present. The existing plugin is still not configured for these endpoints.

Old schema1 output receives only the corrected releasedAt and releaseStatus fields for this pair, not the new policy field. Its history is byte-identical. The pinned old PHP parser does not read release metadata and continues its pre-existing current-state fallback before release. It cannot express absence, and no plugin behavior or global visibility setting is changed here.

Run python3 tools/test-dk-availability.py in addition to the full suite. It checks November 29, November 30, December 7 and surrounding dates, strict confidence rejection, unknown policies, all precise policy exports, future interval boundaries, unchanged old fallback and 1,200 unchanged date cases across the other 150 cards. Clean migration deterministically reproduces the correction.
