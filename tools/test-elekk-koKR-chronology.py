#!/usr/bin/env python3
"""Regression for King's Elekk original koKR wording and 12.2 text-only revision."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

cid, dbf = "AT_058", "2635"
timeline = read("data/AT_058.json")
meta = read("metadata/AT_058.json")
observed = meta["supplementalAudit"]["document"]["historicalTextObservations"]
old_ko = next(x["rawText"] for x in observed if x["build"]=="3.0.0.9786")
raw_new = next(x["rawText"] for x in observed if x["build"]=="12.2.0.26996")
new_ko = raw_new.replace("전투의_함성", "전투의 함성")

assert list(timeline)==["2015-08-25","2018-10-03"]
assert (timeline["2015-08-25"]["id"],timeline["2015-08-25"]["dbfId"])==(cid,2635)
assert timeline["2015-08-25"]["text"]==old_ko
assert timeline["2018-10-03"]=={"text":new_ko}
assert "하수인 하나를" in old_ko
assert "하수인 하나를" not in new_ko
assert meta["release"]=={"date":"2015-08-25","status":"verified"}
assert meta["originalSource"]["card"]["id"]==cid
assert meta["currentCatalog"]["text"]==raw_new
assert meta["historicalTextCorrection"]["adoptedDisplayChangeKst"]=="2018-10-03"
assert meta["historicalTextCorrection"]["dateConfidence"]=="estimated-card-specific"

revision=[{"before":"2018-10-03","changes":{"text":old_ko},"from":"2015-08-25"}]
for filename in ("cards.json","cards-date.json","render.json","render-date.json"):
    card=next(x for x in read(filename)["cards"] if x["id"]==cid)
    assert card["text"]==new_ko, (filename,"current text")
    assert card["releasedAt"]=="2015-08-25"
    if filename.startswith("render"):
        assert card["history"]==revision,(filename,"history")

old=read("history.json")["cards"][dbf]
assert old=={"id":cid,"history":revision}
precise=read("history-date.json")["cards"][dbf]
assert precise["current"]["text"]==new_ko
assert precise["history"]==revision
assert precise["releasedAt"]=="2015-08-25"

def lookup(day, history):
    text=new_ko
    for event in history:
        if event.get("from","0001-01-01")<=day<event["before"]:
            text=event["changes"]["text"]
    return text

for d in ["2015-08-25","2018-04-11","2018-10-02"]:
    assert lookup(d,revision)==old_ko,d
for d in ["2018-10-03","2026-11-14"]:
    assert lookup(d,revision)==new_ko,d

assert len(read("cards.json")["cards"])==148
print(json.dumps({"result":"pass","id":cid,"launch":"2015-08-25",
    "wordingDate":"2018-10-03","dateConfidence":"estimated-card-specific",
    "reverseHistoryInterfaces":4},ensure_ascii=False))
