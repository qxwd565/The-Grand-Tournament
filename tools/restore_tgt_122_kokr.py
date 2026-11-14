#!/usr/bin/env python3
"""Bounded correction of TGT koKR release descriptions first simplified in 12.2.

Only the 23 independently pre-audited cards with a single 12.0->12.2 observed
change range are eligible. This dates *display wording* tentatively on Korean
12.2 launch, not an undocumented gameplay buff or balance change.
"""
from __future__ import annotations
import copy
import json
import re
from pathlib import Path
from date_schema import fold,load,put,validate_timeline

ROOT=Path(__file__).resolve().parents[1]
IDS=("AT_002", "AT_004", "AT_005", "AT_009", "AT_010", "AT_022", "AT_023", "AT_035", "AT_038", "AT_040", "AT_077", "AT_078", "AT_084", "AT_094", "AT_099", "AT_100", "AT_104", "AT_106", "AT_108", "AT_112", "AT_113", "AT_131", "AT_133")
FIRST="2015-08-25"
WORDING_DAY="2018-10-03"
KOREA_PATCH="https://hearthstone.blizzard.com/ko-kr/news/22546493"

def normalized(text):
    text=str(text)
    text=text.replace("\r\n","\n").replace("\\r\\n","\n").replace("\\n","\n")
    text=re.sub(r"(?<![A-Za-z])/n","\n",text)
    text=re.sub(r"<br\s*/?>\s*(?:</br\s*>)?|</br\s*>","<br></br>",text,flags=re.I)
    return (text.replace("\n","<br></br>")
            .replace("전투의_함성","전투의 함성")
            .replace("죽음의_메아리","죽음의 메아리")
            .replace("천상의_보호막","천상의 보호막"))

def loose(text):
    return re.sub(r"\s+","",normalized(text).replace("[x]","").replace("<br></br>",""))

def migrate(root=ROOT):
    corrected=[]
    for cid in IDS:
        path=root/"data"/f"{cid}.json"
        mp=root/"metadata"/f"{cid}.json"
        meta=load(mp);timeline=load(path)
        obs=meta["supplementalAudit"]["document"]["historicalTextObservations"]
        launch=next((x for x in obs if x["build"]=="3.0.0.9786"),None)
        twelve=next((x for x in obs if x["build"]=="12.2.0.26996"),None)
        if not launch or not twelve:raise ValueError(cid+": missing exact archival koKR observation")
        audit=load(root/"tools/tgt-release-audit.json")
        card=next(x for x in audit["cards"] if x["id"]==cid)
        ranges=card["observedTextTransitionRanges"]
        if not (len(ranges)==1 and ranges[0]["afterObservedBuild"]=="12.0.0.25770"
          and ranges[0]["byObservedBuild"]=="12.2.0.26996"):
            raise ValueError(cid+": transition source no longer satisfies conservative cohort")
        original=normalized(launch["rawText"])
        assert list(timeline)==sorted(timeline) and next(iter(timeline))==FIRST,cid
        if any(FIRST<d<WORDING_DAY for d in timeline):raise ValueError(cid+": earlier patch would be overwritten")
        before=timeline[FIRST]["text"]
        post=timeline[WORDING_DAY]["text"] if WORDING_DAY in timeline else before
        if not loose(post)==loose(twelve["rawText"]):raise ValueError(cid+": canonical post-revision text differs semantically from archived 12.2")
        if loose(original)==loose(post):raise ValueError(cid+": no actual wording difference from launch")
        if before not in (original,post,twelve["rawText"]) and normalized(before)!=post:
            raise ValueError(cid+": launch text has an unreviewed change")
        if WORDING_DAY in timeline and timeline[WORDING_DAY]!={"text":post}:raise ValueError(cid+": 12.2 patch has unreviewed fields")
        latest=fold(timeline)
        if latest["id"]!=cid or latest["dbfId"]!=meta["currentCatalog"]["dbfId"]:raise ValueError(cid+": identity changed")
        updated={FIRST:{**timeline[FIRST],"text":original}, WORDING_DAY:{"text":post}}
        for d,v in timeline.items():
            if d not in (FIRST,WORDING_DAY):updated[d]=copy.deepcopy(v)
        updated=dict(sorted(updated.items()))
        validate_timeline(updated)
        now=fold(updated)
        if {k:v for k,v in now.items() if k!="text"}!={k:v for k,v in latest.items() if k!="text"}:
            raise ValueError(cid+": modern gameplay or nontext card state drifted")
        if normalized(now["text"])!=normalized(latest["text"]):
            raise ValueError(cid+": modern card wording drifted outside audited display normalization")
        put(path,updated)
        meta["historicalTextCorrection"]={
          "purpose":"Reconstruct 3.0 launch koKR and preserve the 12.2 observed wording in a separate dated diff, without changing gameplay",
          "originalFirstPlayableKst":FIRST,
          "adoptedDisplayChangeKst":WORDING_DAY,
          "dateConfidence":"estimated-card-specific",
          "dateBasis":"Only the 12.0.0.25770 -> 12.2.0.26996 localized client interval is observed, not a dated Korean screenshot. Patch 12.2 KST date is used provisionally.",
          "sourceArchivedClientBuilds":[
             {"build":launch["build"],"koKR":launch["rawText"],"source":launch["source"]},
             {"build":twelve["build"],"koKR":twelve["rawText"],"source":twelve["source"]}
          ],
          "koreaPatchEvidence":[KOREA_PATCH],
          "immutableOriginalSourcePreserved":True,
          "currentGameplayFieldsChanged":[],
          "source":"tools/tgt-release-audit.json",
        }
        put(mp,meta)
        corrected.append(cid)
    print(json.dumps({"corrected":corrected,"count":len(corrected),
      "wordingDay":WORDING_DAY,"confidence":"estimated-card-specific"},ensure_ascii=False))

if __name__=="__main__":migrate()
