# Architecture

```text
Web form → HTTP API → Project Analyzer → Harness Builder
                                      → Planning Engine → Tools → Validator
                                                        ↓
                                                Structured Result
```

- Web UI는 구조화 입력과 결과 표시만 담당합니다.
- API는 입력 검증, 계획 요청 전달, 오류 응답을 담당합니다.
- Harness Builder는 `knowledge/`의 공통·장르·엔진 지식에서 프로젝트에 필요한 Context, Rule, Tool, Workflow를 선택합니다.
- Planning Engine은 장르별 태스크를 만들고 등록된 계산 도구로 담당자를 배정합니다.
- Validator는 필수 태스크, 담당자, 가용 시간, 의존성, 결과 구조를 검사합니다.
- 수정 요청은 기존 입력을 유지한 채 추가 제약조건으로 해석하여 재계산합니다.

현재 Planning Engine은 재현 가능한 규칙 기반 구현입니다. 향후 LLM은 태스크 후보와 배정 근거의 자연어 판단만 담당하고, 점수 계산과 검증은 동일한 도구 계층에 유지합니다.
