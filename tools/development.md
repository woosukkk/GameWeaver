# Development tools

## Ponytail

- Source: [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)
- Status: 기본 사용
- Form: Codex/Claude Code 등에서 사용하는 플러그인과 스킬
- Use for: YAGNI, 기존 코드·표준 기능 우선, 과설계 방지, 최소 구현 및 복잡도 검토

프로젝트에 코드를 복사하지 않고 사용자 환경의 전역 플러그인으로 사용합니다. 현재 Codex 환경에는 이미 설치되어 있습니다.

## Code Review Graph

- Source: [tirth8205/code-review-graph](https://github.com/tirth8205/code-review-graph)
- Status: 조건부 사용
- Form: CLI와 MCP 서버
- Use for: 대규모 저장소의 구조 분석, 변경 영향 범위, 관련 테스트 탐색, PR 리뷰 컨텍스트 축소

작은 신규 프로젝트에는 기본 설치하지 않습니다. 저장소 탐색이나 리뷰 비용이 커질 때 프로젝트별로 도입합니다.
