#!/usr/bin/env python3
"""Verify all first Korean playable dates, including pre-release Tavern Brawl and generated children."""
from pathlib import Path
from collections import Counter
import json
ROOT=Path(__file__).resolve().parents[1]
def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
def main():
    audit=load("tools/tgt-first-availability-20261114.json")
    modern={x["id"]:x for x in load("cards-date.json")["cards"]}
    legacy={x["id"]:x for x in load("cards.json")["cards"]}
    assert audit["timezone"]=="Asia/Seoul"
    assert len(modern)==len(legacy)==len(audit["records"])==152
    assert len([c for c in modern.values() if c["collectible"]])==132
    assert {x.stem for x in (ROOT/"data").glob("*.json") if x.stem!="history"}==set(modern)
    assert {x.stem for x in (ROOT/"metadata").glob("*.json")}==set(modern)
    assert audit["modeDates"]["KoreanPremadeTavernBrawl"]=="2015-08-20"
    assert audit["modeDates"]["KoreanConstructed"]=="2015-08-25"
    decks=audit["brawlDecks"]
    assert len(decks["Medivh"])==18 and len(decks["Alleria"])==11
    assert not set(decks["Medivh"])&set(decks["Alleria"])
    children=audit["brawlGeneratedChildren"]
    assert children=={"AT_005t":"AT_005","AT_099t":"AT_099"}
    preview=set(decks["Medivh"]+decks["Alleria"]+list(children))
    assert len(preview)==31
    counts=Counter();seen=set()
    for row in audit["records"]:
        cid=row["id"]
        assert cid in modern and cid not in seen,cid
        seen.add(cid)
        card=modern[cid]
        assert row["name"]==card["name"] and row["dbfId"]==card["dbfId"]==legacy[cid]["dbfId"],cid
        assert row["collectible"]==card["collectible"]
        assert row["constructedReleaseKst"]==card["releasedAt"]==legacy[cid]["releasedAt"],cid
        assert row["canonicalReleaseStatus"]==card["releaseStatus"]
        timeline=load("data/"+cid+".json")
        metadata=load("metadata/"+cid+".json")
        assert next(iter(timeline))==card["releasedAt"],cid
        assert metadata["release"]["date"]==card["releasedAt"],cid
        assert metadata["release"]["status"]==card["releaseStatus"],cid
        first=row["earliestPlayableKst"]
        counts[first]+=1
        if cid in preview:
            assert first=="2015-08-20" and card["releasedAt"]=="2015-08-25"
            if cid in children:
                assert row["generatedBy"]==children[cid]
                assert row["firstPlayableMode"]=="brawl-parent-generated"
                assert children[cid] in decks["Medivh"] and not card["collectible"]
            else:
                assert card["collectible"]
                assert row["firstPlayableMode"]=="preconstructed-tavern-brawl"
                assert row["brawlDeck"]==("Medivh" if cid in decks["Medivh"] else "Alleria")
        elif cid=="OG_044c":
            assert first=="2016-04-27" and not card["collectible"]
        elif cid in ("HERO_11bp2","HERO_11bp2t"):
            assert first=="2022-11-30" and card["releaseStatus"]=="estimated"
            assert row["firstPlayableConfidence"]=="estimated"
            assert metadata["release"].get("beforeDate")=="unavailable"
        else:
            assert first=="2015-08-25" and card["releasedAt"]=="2015-08-25",cid
    assert seen==set(modern)
    assert counts==Counter({"2015-08-20":31,"2015-08-25":118,"2016-04-27":1,"2022-11-30":2})
    assert dict(counts)==audit["counts"]["firstPlayableByDate"]
    assert "AT_132_SHAMANe" not in modern
    print(json.dumps({"result":"pass","total":152,"brawlPreview":31,"firstConstructedOnly":118,"Fandral":1,"DK_qualified":2,"cardDatesChanged":0}))
if __name__=="__main__":
    main()
