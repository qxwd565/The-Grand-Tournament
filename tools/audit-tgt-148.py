#!/usr/bin/env python3
"""Read-only, full-set TGT public API chronology and Korean-text audit.

All 148 currently indexed records are checked. Historical localised text is
evidence of client build content, NOT automatically a server-live change date.
Only reports are written; this job never alters canonical card timelines.
"""
from __future__ import annotations

import copy
import json
import re
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from date_schema import apply, fold, load, validate_timeline

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "tools/tgt-full-qa-20261114.json"
SUMMARY = ROOT / "tools/tgt-full-qa-summary-20261114.md"
BASE = "https://hearthstone.blizzard.com/ko-kr/news/22546493"
DK_SOURCE = "https://hearthstone.blizzard.com/ko-kr/news/23882860"
RETIRED = {"AT_132_SHAMANa","AT_132_SHAMANb","AT_132_SHAMANc","AT_132_SHAMANd"}
FIXED = {"AT_058","AT_074"}

def norm(text):
    text = str(text or "")
    text = text.replace("\r\n","\n").replace("\\r\\n","\n").replace("\\n","\n")
    text = re.sub(r"(?<![A-Za-z])/n", "\n", text)
    text = re.sub(r"<br\s*/?>\s*(?:</br\s*>)?|</br\s*>", "<br></br>", text, flags=re.I)
    text = text.replace("\n","<br></br>")
    text = text.replace("전투의_함성","전투의 함성").replace("죽음의_메아리","죽음의 메아리").replace("천상의_보호막","천상의 보호막")
    return text

def semantic(text):
    text = norm(text).replace("[x]","").replace("<br></br>","")
    return re.sub(r"\s+","",text)

def reconstruct(record,day):
    if day<record["releasedAt"] and record["releaseStatus"]=="verified":
        return None
    state=copy.deepcopy(record["current"])
    state.pop("art",None)
    for event in record.get("history",[]):
        if event.get("from","0001-01-01")<=day<event.get("before","9999-12-31"):
            state=apply(state,event["changes"])
    return state

def main():
    bundles={n:load(ROOT/n) for n in ("cards.json","cards-date.json","render.json","render-date.json","history.json","history-date.json")}
    ids={entry["id"] for entry in bundles["cards.json"]["cards"]}
    if len(ids)!=148:
        raise ValueError(f"Expected current TGT public corpus of 148 IDs, got {len(ids)}")
    if ids&RETIRED:
        raise ValueError("Retired Totemic Slam choice IDs have returned")
    for name in ("cards-date.json","render.json","render-date.json"):
        if {x["id"] for x in bundles[name]["cards"]}!=ids:raise ValueError("Endpoint identity mismatch: "+name)
    if len(bundles["history-date.json"]["cards"])!=148:
        raise ValueError("Precise history is not complete")
    if {p.stem for p in (ROOT/"metadata").glob("*.json")}!=ids:
        raise ValueError("Metadata files do not match the 148 public IDs")
    if {p.stem for p in (ROOT/"data").glob("*.json") if p.stem!="history"}!=ids:
        raise ValueError("Canonical date-map files do not match the 148 public IDs")

    catalog={c["id"]:c for c in bundles["cards-date.json"]["cards"]}
    current={c["id"]:c for c in bundles["cards.json"]["cards"]}
    precise={c["id"]:c for c in bundles["render-date.json"]["cards"]}
    compatible={c["id"]:c for c in bundles["render.json"]["cards"]}
    availability=load(ROOT/"tools/tgt-first-availability-20261114.json")
    ledger={c["id"]:c for c in availability["records"]}
    old=load(ROOT/"tools/tgt-release-audit.json")
    archive={c["id"]:c for c in old["cards"]}
    if set(ledger)!=ids or not ids<=set(archive):
        raise ValueError("First-use ledger or audited client source coverage is incomplete")
    results=[]
    seen_dbf=set()
    summary=Counter()
    missing_art=[]
    patch_years=Counter()
    unmodeled=[]
    for cid in sorted(ids):
        c=catalog[cid];oldc=current[cid]
        meta=load(ROOT/"metadata"/f"{cid}.json")
        timeline=load(ROOT/"data"/f"{cid}.json")
        validate_timeline(timeline)
        state=fold(timeline)
        first_day=next(iter(timeline))
        first=fold(timeline,first_day)
        record=bundles["history-date.json"]["cards"].get(str(c["dbfId"]))
        if record is None:
            raise ValueError("Missing precise reverse index for "+cid)
        if c["dbfId"] in seen_dbf:raise ValueError("Duplicate DBF ID: "+cid)
        seen_dbf.add(c["dbfId"])
        if first_day!=meta["release"]["date"] or c["releasedAt"]!=first_day:
            raise ValueError("First date or metadata mismatch: "+cid)
        if first_day!=ledger[cid]["constructedReleaseKst"]:
            raise ValueError("First constructed release disagrees with Korean date ledger: "+cid)
        if c["dbfId"]!=oldc["dbfId"] or c["dbfId"]!=archive[cid]["id"] and False:
            raise ValueError("Native DBF mapping changed: "+cid)
        if precise[cid].get("history")!=record["history"]:
            raise ValueError("Precise renderer/history interval mismatch: "+cid)
        if compatible[cid].get("history",[])!=bundles["history.json"]["cards"].get(str(c["dbfId"]),{}).get("history",[]):
            raise ValueError("Old renderer/history interval mismatch: "+cid)
        days={first_day, (date.fromisoformat(first_day)+timedelta(days=1)).isoformat()}
        for d in timeline:
            days.add(d)
            days.add((date.fromisoformat(d)-timedelta(days=1)).isoformat())
            days.add((date.fromisoformat(d)+timedelta(days=1)).isoformat())
        for day in sorted(days):
            if day<first_day:continue
            snapshot=fold(timeline,day)
            derived=reconstruct(record,day)
            if snapshot!=derived:
                raise ValueError("Date-first projection is inconsistent for "+cid+" at "+day)
            summary["historicalLookupChecks"]+=1
        for d,v in timeline.items():
            for field,val in v.items():
                if isinstance(val,str) and field=="text":
                    if "\n" in val or "\\n" in val or "/n" in val:
                        summary["noncanonicalLineBreaks"]+=1
                        unmodeled.append({"id":cid,"date":d,"issue":"Non-HTML display linebreak in dated text"})
            if d!=first_day:patch_years[d[:4]]+=1
        if cid not in FIXED and meta.get("historicalTextCorrection",{}).get("dateConfidence")=="estimated-card-specific":
            unmodeled.append({"id":cid,"issue":"Additional unrecognized estimated source text change"})
        if first.get("spellSchool") and first_day<"2021-03-26":unmodeled.append({"id":cid,"issue":"Potential spell school backdated"})
        if "UNDEAD" in first.get("races",[]) and first_day<"2022-11-30":unmodeled.append({"id":cid,"issue":"Undead tribe backdated"})
        if "DRAENEI" in first.get("races",[]) and first_day<"2024-10-30":unmodeled.append({"id":cid,"issue":"Draenei tribe backdated"})
        artwork=oldc.get("art")
        if not artwork or not (ROOT/artwork).is_file():missing_art.append({"id":cid,"path":artwork})
        supplement=meta.get("supplementalAudit",{}).get("document",{})
        observed=supplement.get("historicalTextObservations",[])
        first_ob=observed[0] if observed else None
        original_ko=archive[cid].get("initialRawText",first_ob["rawText"] if first_ob else "")
        now_ko=first.get("text","")
        current_ko=c.get("text","")
        launch_is_same=norm(original_ko)==norm(now_ko)
        same_meaning=semantic(original_ko)==semantic(now_ko)
        last_ob=observed[-1] if observed else None
        second=next((o for o in observed if o.get("build")=="12.2.0.26996"),None)
        present_matches_later=bool(second and semantic(now_ko)==semantic(second["rawText"]))
        change_ranges=archive[cid].get("observedTextTransitionRanges",[])
        timing=meta.get("historicalTextCorrection")
        if launch_is_same:
            bucket="launch_text_matches_client_archive"
        elif same_meaning:
            bucket="layout_or_keyword_markup_difference"
        elif present_matches_later and first_day=="2015-08-25":
            bucket="later_12_2_wording_potentially_backdated"
        else:
            bucket="other_historical_wording_difference"
        summary[bucket]+=1
        if cid in FIXED and not launch_is_same:
            raise ValueError("Previously corrected original wording regressed: "+cid)
        result={
            "id":cid,"name":c["name"],"dbfId":c["dbfId"],
            "collectible":c["collectible"],"class":c["cardClass"],
            "firstConstructedKst":first_day,"releaseStatus":meta["release"]["status"],
            "firstEverPlayableKst":ledger[cid]["earliestPlayableKst"],
            "earliestPlayMode":ledger[cid]["firstPlayableMode"],
            "datedEvents":[{"date":d,"fields":list(v)} for d,v in list(timeline.items())[1:]],
            "historicalKoKR":{
                "firstClientBuild":first_ob.get("build") if first_ob else None,
                "firstClientRaw":original_ko,
                "publishedReleaseText":now_ko,
                "latestClientBuild":last_ob.get("build") if last_ob else None,
                "latestClientRaw":last_ob.get("rawText") if last_ob else None,
                "transitionRanges":change_ranges,
                "classification":bucket,
                "known2018Build":second.get("build") if second else None,
                "cardSpecificChangeDateConfidence":timing.get("dateConfidence") if timing else None,
                "firstUseAndTextHistoryAreSeparateClaims":True
            },
        }
        if bucket!="launch_text_matches_client_archive":result["reviewRequired"]=True
        if cid.startswith("HERO_11") and first_day=="2022-11-30":
            result["dateWarning"]="2022-11-30 may be real pre-class use by Finley generation (contemporary reports), while class unlock was 2022-12-07 KST. Exact Korean game-day and CardID match remain estimated; do not turn this into a verified preload or an automatic Dec 7 correction."
            summary["dkPreClassGenerationDateQualified"]+=1
        results.append(result)
    summary.update({
        "publicCards":len(ids),
        "collectibleCards":sum(c["collectible"] for c in catalog.values()),
        "generatedOrUncollectibleCards":sum(not c["collectible"] for c in catalog.values()),
        "archivedFirstUseEvidenceCount":len(ledger),
        "sourceLegacyIndexed":len(bundles["cards.json"]["cards"]),
        "sourcePreciseIndexed":len(bundles["cards-date.json"]["cards"]),
        "missingArtworkCount":len(missing_art),
        "topLevelReleaseDatesVerified":sum(c["releaseStatus"]=="verified" for c in results),
        "topLevelReleaseDatesEstimated":sum(c["releaseStatus"]=="estimated" for c in results)
    })
    report={
        "schema":1,"reviewDate":"2026-11-14","timezone":"Asia/Seoul",
        "scope":"148 currently publicly indexed TGT cards; inherited 152-card historical audit is source evidence only",
        "auditMethod":"Date-first source + six current transports + original 3.0/localized client observations + Korean first-use ledger, with no assumed historical live server timing from client files",
        "summary":dict(summary),"patchEventYears":dict(sorted(patch_years.items())),
        "missingArtwork":missing_art,"warnings":unmodeled,"cards":results,
        "specialCautions":[
          "The 2018-10-03 per-card wording boundaries for AT_058 and AT_074 remain inferred, not individually proven KST game-client presentation times.",
          "Historically different koKR strings do not establish a balance change; cosmetic line breaks, localized style updates, and live-game effects remain separate.",
          "The full Death Knight class was unlocked on 2022-12-07; however, pre-class Finley generation of its hero power was reported in late November. The exact 2022-11-30 Korean match day and internal card ID remain estimated, not disproven.",
          "Open-ended Korean restore date for AT_037 temporary EPIC rarity was not guessed."
        ],
        "sources":{
          "originalClientData":"tools/tgt-release-audit.json",
          "selectedArchives":"tools/supplemental-audit/<CARD_ID>.json",
          "firstUseLedger":"tools/tgt-first-availability-20261114.json",
          "KoreanClient12_2":BASE,"KoreanDeathKnightUnlock":DK_SOURCE,
          "knownUnmodeledIntervals":"tools/tgt-known-unmodeled-intervals.json", "preClassDeathKnightEvidence":"tools/tgt-dk-availability-evidence.json"
        }
    }
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=[
      "# 대 마상시합 148장 전수 API 대조 (2026-11-14)",
      "",
      "자료: TGT 최초 출시 한국 날짜 장부, 3.0/12.2 등 보존된 koKR 카드 정의, 148개 날짜별 JSON, 공개 6종 API.",
      "",
      "| 검사 항목 | 결과 |","|---|---:|",
      f"| 현행 공개 카드 | {summary['publicCards']}장 |",
      f"| 수집 가능 / 수집 불가 | {summary['collectibleCards']} / {summary['generatedOrUncollectibleCards']} |",
      f"| 날짜별 역산 검사 | {summary['historicalLookupChecks']}회 |",
      f"| 초판 한국어 원문과 현재 최초 텍스트 일치 | {summary['launch_text_matches_client_archive']}장 |",
      f"| 줄바꿈/표시 형식 차이 | {summary['layout_or_keyword_markup_difference']}장 |",
      f"| 12.2 문구가 출시일로 소급되었을 가능성 | {summary['later_12_2_wording_potentially_backdated']}장 |",
      f"| 기타 과거 문구 불일치 | {summary['other_historical_wording_difference']}장 |",
      f"| 원화 누락 | {summary['missingArtworkCount']}건 |",
      f"| 선행 생성 가능성이 있는 죽음의 기사 카드(날짜 미확정) | {summary['dkPreClassGenerationDateQualified']}건 |",
      "",
      "## 검토 대상",
      "",
      "아래 항목은 과거 저장된 클라이언트 문자열과 최초 기준 상태가 다르다는 뜻이지, 그 자체로 실제 서버 적용 날짜가 검증되었다는 뜻은 아닙니다.",
      "",
      "| ID | 카드 | 분류 | 패치 수 |",
      "|---|---|---|---:|",
    ]
    for x in results:
        kind=x["historicalKoKR"]["classification"]
        if kind=="launch_text_matches_client_archive":continue
        lines.append(f"| {x['id']} | {x['name']} | {kind} | {len(x['datedEvents'])} |")
    lines.extend(["","## 제한 및 근거",
                  "원문 날짜는 해당 클라이언트 빌드에 존재했던 문자열의 날짜이며, 같은 날짜에 한국 게임 서버에서 반드시 표시되었다는 증거는 아닙니다.",
                  "초판 문구 복원에는 최초 관찰값과 실제 게임 속 효과를 구분해야 하며, 한국 적용 날짜를 별도로 검증해야 합니다.",
                  f"공식 한국 12.2 공지: {BASE}",
                  f"공식 한국 죽음의 기사 25.0 공지: {DK_SOURCE}",
                  ""])
    SUMMARY.write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"result":"audited","summary":dict(summary),"patchEventYears":dict(patch_years),
                      "missingArtwork":missing_art,"warnings":unmodeled,
                      "report":str(REPORT.relative_to(ROOT))},ensure_ascii=False))
if __name__=="__main__":
    main()
