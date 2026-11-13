# Date-first API update

See [docs/date-schema.md](docs/date-schema.md) for canonical card files, precise endpoints, compatible root transports, provenance, known uncertainties and reproducible tests. `data/history.json` is retained noncanonical legacy evidence, not a card record.

# HSdeck The Grand Tournament 카드 API

`cards.json`과 `render.json`은 기존 HS Plus 카드 정보를 기반으로 하며, `art/`는 설치된 클라이언트의 원화입니다. `golden/`은 해당 카드의 원본 황금 원화 재질·애니메이션·텍스처입니다. 날짜별 과거 원화나 황금 효과를 보장하지 않습니다.

## 한국 최초 실사용 가능일 재검증 (2026-11-14)

카드 최초 실제 게임모드 사용 가능일과 일반 덱 보유·제작 가능일을 별도로 기록합니다. 상세 152개 기록: tools/tgt-first-availability-20261114.json.

2015-08-20: 메디브/알레리아 선술집 난투 고정 덱에 들어간 대 마상시합 수집 카드 29개와 메디브가 조건부 생성하는 멧돼지 AT_005t, 전투코도 AT_099t 2개, 합계 31개. 한국 실제 난투 개방일은 전자신문 2015-08-20 당시 보도로 확인했습니다. 2015-08-25: 그 외 당시 신규 118개와 전체 132개 수집 카드의 정식 카드팩·제작·일반 덱 해금일. 2016-04-27: 판드랄 전용 칼날이빨의 드루이드 합체형 OG_044c. 2022-11-30: 죽음의 기사 강화 영웅 능력 및 구울 2개(추정; 직접 플레이 증거 부족).

기존 data/<ID>.json 및 releasedAt은 일반 덱 기준이어서 그대로 보존했습니다. 실사용 가능일은 날짜별 검증 파일에 별도 기록했으며 난투 카드를 8월 20일부터 제작 가능했던 것으로 허위 표시하지 않습니다. CI: python3 tools/test-tgt-first-availability.py. 최초 한국어 설명, 밸런스 패치, 기존 원본 증거는 수정하지 않았습니다. 미등록 AT_132_SHAMANe는 출처·원화가 확인되기 전 임의로 생성하지 않습니다.
