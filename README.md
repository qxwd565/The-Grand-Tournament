# Date-first API update

See [docs/date-schema.md](docs/date-schema.md) for canonical card files, precise endpoints, compatible root transports, provenance, known uncertainties and reproducible tests. `data/history.json` is retained noncanonical legacy evidence, not a card record.

# HSdeck The Grand Tournament 카드 API

`cards.json`과 `render.json`은 기존 HS Plus 카드 정보를 기반으로 하며, `art/`는 설치된 클라이언트의 원화입니다. `golden/`은 해당 카드의 원본 황금 원화 재질·애니메이션·텍스처입니다. 날짜별 과거 원화나 황금 효과를 보장하지 않습니다.

## 한국 최초 실사용 가능일 재검증 (2026-11-14)

카드 최초 실제 게임모드 사용 가능일과 일반 덱 보유·제작 가능일을 별도로 기록합니다. 상세 152개 기록: tools/tgt-first-availability-20261114.json.

2015-08-20: 메디브/알레리아 선술집 난투 고정 덱에 들어간 대 마상시합 수집 카드 29개와 메디브가 조건부 생성하는 멧돼지 AT_005t, 전투코도 AT_099t 2개, 합계 31개. 한국 실제 난투 개방일은 전자신문 2015-08-20 당시 보도로 확인했습니다. 2015-08-25: 그 외 당시 신규 118개와 전체 132개 수집 카드의 정식 카드팩·제작·일반 덱 해금일. 2016-04-27: 판드랄 전용 칼날이빨의 드루이드 합체형 OG_044c. 2022-11-30: 죽음의 기사 강화 영웅 능력 및 구울 2개(추정; 직접 플레이 증거 부족).

기존 data/<ID>.json 및 releasedAt은 일반 덱 기준이어서 그대로 보존했습니다. 실사용 가능일은 날짜별 검증 파일에 별도 기록했으며 난투 카드를 8월 20일부터 제작 가능했던 것으로 허위 표시하지 않습니다. CI: python3 tools/test-tgt-first-availability.py. 최초 한국어 설명, 밸런스 패치, 기존 원본 증거는 수정하지 않았습니다. 미등록 AT_132_SHAMANe는 출처·원화가 확인되기 전 임의로 생성하지 않습니다.

### 트루하트 주술사 힘의 토템 선택지 날짜 (2026-11-14)

기존 강화 영웅 능력 HERO_02bp2는 고전 API에 2015-08-25부터 기록되어 있습니다. 선택지 AT_132_SHAMANa/b/c/d는 TGT에 존재하지만, 2021년 생긴 AT_132_SHAMANe (DBF 72268)는 아직 미등록입니다. 해당 선택지의 최초 사용 가능 날짜를 실제 소환 하수인 CS2_058 (고전 API, DBF 62320)의 한국 첫 날짜와 일치하도록 2021-03-31로 확정하여 tools/tgt-missing-ids.json에 기록하고 CI 검증에 묶었습니다. 20.0 클라이언트 선행 추가일은 출시일로 기록하지 않습니다. 정확한 원본 선택지 원화·메타데이터가 없으므로 불완전한 data/카드를 조작해서 API에 넣지는 않았습니다. 현재 전체 저장소는 여전히 152개 인덱스이고, 이 선택지의 정식 등록은 자산 확인 뒤 남은 작업입니다.

## 2026-11-14 강화 영웅 능력·힘의 토템 선택지 세트 확인

공식 카드 분류는 트루하트 본체 `AT_132`와 `AT_132_SHAMANa`~`e` 선택지는 TGT, 업그레이드된 기본 영웅 능력 `HERO_01bp2`~`HERO_09bp2`는 현재 Legacy다. 원래 `AT_132_SHAMAN` 등 영웅 능력 ID는 2020-05-12 패치에서 `HERO_XXbp2`로 재식별됐다. 따라서 Legacy의 현대 원본 ID를 TGT로 이동하거나 복제하지 않았다.

지시한 힘의 토템 선택지 `AT_132_SHAMANe`의 날짜별 JSON 초안을 `data/_pending/AT_132_SHAMANe.json`에 생성했다. **아직 API 등록 파일은 아니다**: 실제 선택지 전용 원화를 미확보했고, 고전 `CS2_058`의 2021-03-31 최초 날짜가 블리자드 한국 20.0의 2021-03-26 및 3월 28일 실제 이용 기록보다 늦어 재교정이 필요하다. 출처와 편집 제한은 `tools/tgt-strength-totem-pending-verification.json`에 명시한다. 해당 최초 키는 현재 Legacy 데이터와 동기화하기 위한 잠정값일 뿐 검증 완료가 아니다. 기존 152개 API와 CI, 밸런스 패치 데이터는 유지한다.
