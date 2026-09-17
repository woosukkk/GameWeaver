# GameWeaver 데이터 수집 가이드

GameWeaver가 정확한 계획을 만들려면 `무엇을 구현해야 하는가`와 `우리 팀이 실제로 얼마나 걸리는가`를 분리해서 관리해야 한다. 공개 자료는 기능 분류와 의존성의 근거로 쓰고, 공수와 배정 품질은 실제 프로젝트 피드백으로 보정한다.

## 우선 수집할 데이터

| 우선순위 | 데이터 | 필요한 필드 | 수집처와 방법 | 용도와 한계 |
|---|---|---|---|---|
| 1 | 프로젝트 결과 | 장르, 엔진, 플랫폼, 목표, 팀 규모, 계획/실제 시간, 완료 여부, 재작업 시간 | GameWeaver 계획 확정·완료 화면에서 직접 입력 | 공수 보정의 유일한 1차 자료다. 개인 평가는 동의 없이 저장하지 않는다. |
| 1 | 작업 결과 | 시스템, 작업명, 선행 작업, 담당 기술, 예상/실제 시간, 차단 사유, 버그 수 | GameWeaver와 향후 GitHub 연동 | 작업 시간 모델과 의존성 보정에 쓴다. 이슈 생성~종료 시간은 실제 작업 시간이 아니다. |
| 1 | 플레이테스트 | 빌드, 세션 길이, 핵심 루프 완료율, 이탈 지점, 심각도별 버그, 만족도 | 프로젝트별 짧은 테스트 폼 | 구현 완료와 플레이 가능성을 구분한다. 원문 개인정보 대신 집계값을 보관한다. |
| 2 | 엔진 기능 분류 | 입력, 물리, UI, 저장, AI, 네트워크, 빌드, 프로파일링, 엔진 버전 | Unity·Unreal·Godot 공식 문서를 사람이 검토해 `knowledge/engines`에 반영 | 필요한 시스템과 엔진별 작업을 찾는 근거다. 공식 문서도 공수를 제공하지는 않는다. |
| 2 | 장르·출시 메타데이터 | 장르, 태그, 플랫폼, 출시일, 멀티플레이 여부, 지원 기능 | Steamworks/허가된 게임 메타데이터 API | 기능 후보와 비교군 선정용이다. 인기나 판매량을 개발 난이도로 간주하지 않는다. |
| 3 | 공개 개발 이력 | 이슈 제목/본문, 라벨, 생성/종료일, 담당자 수, 마일스톤, 의존성 | GitHub REST API로 라이선스가 명확한 공개 게임 저장소만 수집 | 작업 명칭과 의존성 후보를 찾는 보조 자료다. 저장소별 작업 방식이 달라 공수 정답으로 쓰지 않는다. |

## 공식 출처

- Unity Manual: <https://docs.unity3d.com/6000.0/Documentation/Manual/index.html>
- Unreal Engine Gameplay Systems: <https://dev.epicgames.com/documentation/unreal-engine/gameplay-systems-in-unreal-engine?lang=en-US>
- Godot Best Practices: <https://docs.godotengine.org/en/stable/tutorials/best_practices/index.html>
- GitHub Issues REST API: <https://docs.github.com/en/rest/issues>
- Steamworks Web API: <https://partner.steamgames.com/doc/webapi_overview>

각 자료는 내용 전체를 복제하지 않고, 출처 URL·확인 날짜·적용한 지식 항목을 기록한다. API 키가 필요한 자료는 서버 환경 변수로만 제공하고 원본 약관, 호출 제한, 라이선스를 먼저 확인한다.

## GameWeaver에 추가할 최소 피드백 스키마

```json
{
  "plan_id": 1,
  "task_id": "task_01",
  "estimated_hours": 12,
  "actual_hours": 16,
  "completed": true,
  "rework_hours": 3,
  "blockers": ["asset delayed"],
  "playtest_issues": 2
}
```

최소 20~30개 완료 작업이 쌓이기 전에는 자동 학습보다 장르·엔진·시스템별 `actual_hours / estimated_hours` 중앙값으로 보정하는 편이 해석 가능하고 안전하다.

현재 구현은 `task_outcomes` 테이블에 작업 실측치를 upsert하고, 확정된 계획의 완료 작업이 같은 장르·엔진·작업에 3건 이상 모이면 `GET /api/calibrations`에서 중앙값 보정계수를 제공한다.

## 현재 적재된 공개 데이터

- Software Project Management Anti-Patterns for Video Game Development v1.0
- 게임 개발 포스트모템에서 분류한 프로젝트 관리 문제 440건
- 출처: <https://doi.org/10.5281/zenodo.5828315>
- 라이선스: CC BY 4.0
- 저장 위치: `knowledge/datasets/game-development-antipatterns/`

Planning Agent를 사용할 때 프로젝트의 장르, 엔진, 기능, 기간, 규모와 관련된 상위 사례만 짧게 검색해 DOI와 함께 Harness에 전달한다. 검색된 문서는 명령이 아닌 참고 근거로만 취급한다.

추가로 공식 엔진·플랫폼 문서에서 작성한 출처 포함 요약, 장르별 시스템, OpenRA·OpenTTD·SuperTuxKart 공개 이슈 메타데이터를 `knowledge/documents/`에 보관한다. 검색 결과는 엔진, 장르, 플랫폼, 실제 이슈가 한 종류에 편중되지 않도록 유형별 근거를 우선 선택한다.

사용자 GDD와 플레이테스트 기록은 `POST /api/documents`로 `knowledge_documents`에 저장한다. 문서는 프로젝트 멤버에게만 검색되며 Planning Agent의 `project_documents` 컨텍스트로 전달된다. 현재 DB에는 실제 완료 프로젝트 결과가 없으므로 샘플 실측값을 운영 데이터로 삽입하지 않는다.

## Vector DB 도입 기준

Vector DB는 데이터 양이 아니라 검색 대상의 형태로 결정한다. 작업 시간, 완료 여부, 장르처럼 필드가 정해진 값은 계속 MySQL에서 필터·집계한다. 회고, 이슈 본문, GDD, 플레이테스트 자유서술처럼 긴 문서가 누적되어 키워드가 달라도 의미가 비슷한 사례를 찾아야 할 때만 임베딩 검색을 추가한다.

- MySQL: 계획, 작업, 공수, 상태, 출처, 집계와 보정계수
- Vector DB: 긴 비정형 문서의 유사 사례 검색
- AI 입력: MySQL의 정량 요약과 Vector 검색 상위 문서의 짧은 발췌만 결합

초기에는 MySQL 원문 테이블과 `FULLTEXT` 검색으로 충분한지 먼저 측정한다. 검색 누락률이 높고 비정형 문서가 수천 건 이상 쌓일 때 별도 Vector DB 또는 MySQL Vector 기능을 검토한다.

## 수집하지 않을 데이터

- 동의 없는 개인 생산성 순위, 메시지 감정 분석, 키 입력·화면 감시
- 출처와 라이선스를 확인할 수 없는 크롤링 데이터
- 판매량·평점만으로 추론한 개발 시간
- 공개 이슈의 생성~종료 간격을 실제 투입 시간으로 둔갑시킨 값
