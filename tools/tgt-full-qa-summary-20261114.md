# 대 마상시합 148장 전수 API 대조 (2026-11-14)

자료: TGT 최초 출시 한국 날짜 장부, 3.0/12.2 등 보존된 koKR 카드 정의, 148개 날짜별 JSON, 공개 6종 API.

| 검사 항목 | 결과 |
|---|---:|
| 현행 공개 카드 | 148장 |
| 수집 가능 / 수집 불가 | 132 / 16 |
| 날짜별 역산 검사 | 671회 |
| 초판 한국어 원문과 현재 최초 텍스트 일치 | 103장 |
| 줄바꿈/표시 형식 차이 | 13장 |
| 12.2 문구가 출시일로 소급되었을 가능성 | 7장 |
| 기타 과거 문구 불일치 | 25장 |
| 원화 누락 | 0건 |
| 죽음의 기사 선행 수록일 의심 | 2건 |

## 검토 대상

아래 항목은 과거 저장된 클라이언트 문자열과 최초 기준 상태가 다르다는 뜻이지, 그 자체로 실제 서버 적용 날짜가 검증되었다는 뜻은 아닙니다.

| ID | 카드 | 분류 | 패치 수 |
|---|---|---|---:|
| AT_003 | 영웅의 넋 | layout_or_keyword_markup_difference | 1 |
| AT_008 | 콜다라 비룡 | layout_or_keyword_markup_difference | 1 |
| AT_013 | 신의 권능: 영광 | other_historical_wording_difference | 1 |
| AT_025 | 어둠의 거래 | layout_or_keyword_markup_difference | 3 |
| AT_026 | 격노수호병 | other_historical_wording_difference | 0 |
| AT_027 | 윌프레드 피즐뱅 | other_historical_wording_difference | 0 |
| AT_031 | 소매치기 | other_historical_wording_difference | 1 |
| AT_032 | 암거래상 | layout_or_keyword_markup_difference | 0 |
| AT_034 | 독 묻은 칼 | other_historical_wording_difference | 1 |
| AT_037 | 살아있는 뿌리 | other_historical_wording_difference | 1 |
| AT_039 | 흉포한 전투원 | layout_or_keyword_markup_difference | 0 |
| AT_043 | 천공의 교감 | later_12_2_wording_potentially_backdated | 2 |
| AT_044 | 양분 흡수 | later_12_2_wording_potentially_backdated | 1 |
| AT_045 | 아비아나 | other_historical_wording_difference | 2 |
| AT_047 | 드레나이 토템술사 | other_historical_wording_difference | 2 |
| AT_050 | 충전된 망치 | layout_or_keyword_markup_difference | 1 |
| AT_054 | 안개소환사 | other_historical_wording_difference | 1 |
| AT_060 | 곰 덫 | other_historical_wording_difference | 0 |
| AT_064 | 강타 | layout_or_keyword_markup_difference | 1 |
| AT_065 | 왕의 수호검 | other_historical_wording_difference | 0 |
| AT_067 | 덩치 큰 마그나타우르 | layout_or_keyword_markup_difference | 0 |
| AT_068 | 고무 | other_historical_wording_difference | 0 |
| AT_069 | 대련 상대 | later_12_2_wording_potentially_backdated | 0 |
| AT_070 | 하늘선장 크라그 | other_historical_wording_difference | 0 |
| AT_072 | 바리안 린 | other_historical_wording_difference | 0 |
| AT_073 | 경쟁심 | layout_or_keyword_markup_difference | 0 |
| AT_076 | 멀록 기사 | later_12_2_wording_potentially_backdated | 0 |
| AT_079 | 수수께끼의 도전자 | other_historical_wording_difference | 1 |
| AT_081 | 성기사 에드릭 | layout_or_keyword_markup_difference | 0 |
| AT_083 | 용매 기수 | layout_or_keyword_markup_difference | 0 |
| AT_086 | 파괴공작원 | other_historical_wording_difference | 0 |
| AT_091 | 마상시합장 의무관 | other_historical_wording_difference | 0 |
| AT_096 | 태엽돌이 기사 | other_historical_wording_difference | 0 |
| AT_103 | 북해 크라켄 | layout_or_keyword_markup_difference | 1 |
| AT_109 | 은빛십자군 경비병 | other_historical_wording_difference | 0 |
| AT_110 | 경기장 관리자 | other_historical_wording_difference | 0 |
| AT_111 | 투스카르 행상인 | other_historical_wording_difference | 0 |
| AT_118 | 고위 성전사 | later_12_2_wording_potentially_backdated | 0 |
| AT_121 | 마상시합 유명인 | other_historical_wording_difference | 0 |
| AT_122 | 꿰뚫는 자 고르목 | other_historical_wording_difference | 0 |
| AT_123 | 서리아귀 | other_historical_wording_difference | 1 |
| AT_124 | 볼프 램실드 | other_historical_wording_difference | 0 |
| AT_127 | 연합용사 사라아드 | later_12_2_wording_potentially_backdated | 0 |
| AT_128 | 해골 기사 | later_12_2_wording_potentially_backdated | 1 |
| AT_130 | 바다의 학살자 | layout_or_keyword_markup_difference | 1 |

## 제한 및 근거
원문 날짜는 해당 클라이언트 빌드에 존재했던 문자열의 날짜이며, 같은 날짜에 한국 게임 서버에서 반드시 표시되었다는 증거는 아닙니다.
초판 문구 복원에는 최초 관찰값과 실제 게임 속 효과를 구분해야 하며, 한국 적용 날짜를 별도로 검증해야 합니다.
공식 한국 12.2 공지: https://hearthstone.blizzard.com/ko-kr/news/22546493
공식 한국 죽음의 기사 25.0 공지: https://hearthstone.blizzard.com/ko-kr/news/23882860
