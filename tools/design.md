# Design skills

## Anthropic Frontend Design

- Source: [anthropics/skills/skills/frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design)
- Status: 프론트엔드 디자인 작업의 기본 스킬
- Use for: 디자인 방향 설정, 타이포그래피와 색상 체계, 개성 있는 프로덕션 UI 구현

## Taste Skill

- Source: [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)
- Status: 프론트엔드 디자인 작업의 보완 스킬
- Use for: 시각적 밀도와 움직임 조절, 일반적인 AI 디자인 패턴 억제, 결과 검토와 개선

## Recommended order

1. Anthropic Frontend Design으로 방향을 정하고 초기 화면을 구현합니다.
2. Taste Skill로 시각적 품질과 일관성을 검토하고 다듬습니다.

두 스킬의 내용을 `AGENTS.md`에 복사하지 않고, 설치된 스킬을 필요한 디자인 작업에서만 사용합니다.

## GameWeaver UI references

21st.dev의 공개 컴포넌트를 화면 구조 참고 자료로 사용한다. React 코드를 프로젝트에 복사하거나 의존성을 추가하지 않고, 현재 `web/`의 HTML/CSS로 필요한 패턴만 재구현한다.

### Project Detail View

- Source: [Kavi Katiyar / Project Detail View](https://21st.dev/@kavikatiyar/components/project-detail-view)
- Use for: 결과 화면의 프로젝트 상태, 요약 지표, 담당자·태스크·일정 정보 구조
- Applied to: `web/index.html`, `web/ui.css`

### AI Planning

- Source: [Arun Dass / AI Planning](https://21st.dev/@arunjdass/components/ai-planning)
- Use for: 계획 생성 중 분석, Harness 구성, 태스크 매칭 진행 상태
- Applied to: `web/index.html`, `web/ui.css`

21st.dev는 공개 컴포넌트를 MIT 라이선스로 안내하지만, 새 자료를 사용할 때는 해당 컴포넌트와 종속 패키지의 라이선스를 다시 확인한다. GameWeaver에는 외부 이미지, 예제 데이터, 원본 소스 코드를 포함하지 않는다.
