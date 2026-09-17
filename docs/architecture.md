# Architecture

```text
Web form → HTTP API → Project Analyzer → Harness Builder ← Knowledge Retriever
                                      → Planning Agent → OpenAI Responses API
                                              ↓                 ↑ retry
                                        Planning Engine → Tools → Validator
                                              ↓
                                      Structured Result → MySQL
```

- Web UI는 구조화 입력과 결과 표시만 담당합니다.
- API는 입력 검증, 계획 요청 전달, 오류 응답을 담당합니다.
- Harness Builder는 `knowledge/`의 공통·장르·엔진 지식에서 프로젝트에 필요한 Context, Rule, Tool, Workflow를 선택합니다.
- Knowledge Retriever는 프로젝트 조건과 관련된 공개 게임 개발 사례를 검색해 출처가 포함된 짧은 근거를 Harness에 추가합니다.
- Planning Engine은 장르별 태스크를 만들고 등록된 계산 도구로 담당자를 배정합니다.
- Validator는 필수 태스크, 담당자, 가용 시간, 의존성, 결과 구조를 검사합니다.
- Planning Agent는 strict JSON Schema로 핵심 루프와 태스크를 생성하며 Validator 오류를 받아 최대 2회 수정합니다.
- AI 키가 없거나 호출이 실패하면 같은 Harness의 규칙 기반 태스크로 안전하게 전환합니다.
- 수정 요청은 기존 입력을 유지한 채 Agent 또는 규칙 엔진의 추가 제약조건으로 해석하여 재계산합니다.
- MySQL은 프로젝트 입력, 결과, 수정 요청, 실측·회고와 사용자별 GDD·플레이테스트 문서를 보존합니다. 문서는 FULLTEXT로 검색해 Planning Agent 컨텍스트에 추가합니다.

LLM은 의미 이해와 태스크 제안만 담당하고, 점수 계산·배정·일정·검증은 재현 가능한 코드 계층에 유지합니다.

현재 RAG 검색은 CC BY 4.0 포스트모템 데이터셋 440건을 대상으로 하는 결정론적 로컬 검색입니다. 데이터 규모가 작아 별도 벡터 DB를 운영하지 않으며, 검색 누락이 측정되고 비정형 문서가 수천 건 이상 쌓일 때 임베딩 검색을 도입합니다.
