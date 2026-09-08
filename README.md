# GameWeaver

Dynamic Harness 기반 게임 개발 태스크·인력 배분 AI입니다. 프로젝트 특성에 맞춰 Context, Rule, Tool, Workflow를 구성하고, 계산 가능한 항목은 코드로 점수화·검증합니다.

> 이 README는 실행 안내이자 프로젝트의 기준 기획서입니다. 개발자와 AI 에이전트는 작업 전에 아래 제품 원칙과 책임 경계를 먼저 확인합니다.

## 제품 정의

GameWeaver는 단순히 LLM에 팀원 정보를 넣고 역할을 추천받는 챗봇이 아니다. 게임 프로젝트의 장르, 엔진, 규모, 일정, 목표와 팀 역량을 분석하고, 그 프로젝트에 필요한 실행 환경을 Dynamic Harness로 구성한 뒤 실제 개발 가능한 태스크와 담당자를 배분하는 서비스다.

주 사용자는 2~6명 규모의 대학생 또는 소규모 인디 게임 개발팀이다. 초기 범위는 게임 개발 프로젝트로 한정하지만, 도메인 지식 모듈을 교체해 다른 프로젝트 유형으로 확장할 수 있어야 한다.

```text
프로젝트·팀 입력
→ 프로젝트 분석
→ Dynamic Harness 구성
→ 태스크 및 요구 역량 생성
→ 팀원 매칭과 배정
→ 계산·검증
→ 근거가 포함된 구조화 결과
→ 사용자 수정 요청을 반영한 재계산
```

핵심 목표는 역할 추천이 아니라 팀이 바로 개발을 시작할 수 있는 현실적인 업무 분담안을 만드는 것이다.

## 핵심 설계 원칙

1. 모든 프로젝트에 같은 프롬프트와 작업 흐름을 적용하지 않는다.
2. 프로젝트 입력은 구조화된 Form 약 70%와 자연어 설명 약 30%로 받는다.
3. Dynamic Harness가 프로젝트별 Context, Rules, Tools, Workflow를 선택한다.
4. Agent는 Harness 안에서만 동작하며 도구와 실행 순서를 임의로 확장하지 않는다.
5. LLM은 의미 이해와 제안에, 일반 코드는 계산과 검증에 사용한다.
6. AI 결과는 설명문만이 아니라 검증 가능한 Structured Output으로 반환한다.
7. 초기 버전은 Single Agent로 완성하며 Multi-Agent를 먼저 도입하지 않는다.
8. 장르·엔진 지식은 코드에 계속 하드코딩하지 않고 교체 가능한 데이터로 발전시킨다.

## 프로젝트별 입력 컨텍스트

사용자로부터 다음 정보를 받는다. 현재 UI에 없는 항목은 향후 입력 모델에 추가한다.

### 게임 프로젝트

- 프로젝트명
- 게임 장르와 참고 게임
- 게임 엔진
- 2D 또는 3D
- 대상 플랫폼
- 팀 규모
- 개발 기간과 마감일
- 프로젝트 목표: MVP, 학습, 포트폴리오, 공모전, 완성작
- 기술 스택
- 핵심 게임 루프와 프로젝트 설명
- 필수 기능과 제외할 기능
- 예상 콘텐츠 규모: 스테이지, 캐릭터, 적, 아이템 등의 수
- 이미 완성된 기능과 보유 에셋
- 우선순위와 외부 제약: 모바일 성능, 무료 에셋, 온라인 기능 제외 등

### 팀원

- 이름 또는 닉네임
- 기술 스택과 기술별 숙련도(0~5)
- 게임 개발 경험과 관련 프로젝트 경험
- 선호 역할과 기피 역할
- 주당 작업 가능 시간
- 학습하고 싶은 분야

숙련도는 팀 안에서 일관된 기준을 사용한다.

```text
0 경험 없음
1 튜토리얼을 따라 해본 수준
2 도움을 받아 작은 작업 가능
3 독립적으로 일반 작업 가능
4 복잡한 작업과 문제 해결 가능
5 설계·리뷰·교육 가능
```

## GameWeaver가 보유해야 할 도메인 컨텍스트

사용자가 매번 설명할 필요가 없는 게임 개발 지식은 GameWeaver 내부 데이터로 관리한다. 초기에는 JSON/YAML 같은 정적 파일로 충분하며, 데이터 규모와 검색 필요성이 확인되기 전에는 Vector DB나 RAG를 도입하지 않는다.

### 공통 개발 단계

```text
기획 → 프로토타입 → Vertical Slice → 콘텐츠 제작 → 통합 → 테스트 → 최적화 → 빌드·배포
```

목표에 따라 필요한 단계와 완료 조건이 달라진다. 예를 들어 짧은 MVP는 핵심 조작과 게임 루프를 우선하고 최종 아트, 대규모 콘텐츠, 세부 최적화를 후순위로 둔다.

### 장르별 시스템

각 장르는 별도의 Context, Workflow, 태스크 후보와 의존성을 가진다.

- Roguelike: Core Loop, Combat, Enemy, Item, Progression, Randomization, Map Generation, Replayability
- Visual Novel: Scenario, Dialogue, Character, Branching Narrative, Save/Load, UI, Localization
- RPG: Character, Quest, Dialogue, Inventory, Combat, Progression, World, Save/Load
- Puzzle: Puzzle Rule, Level Design, Hint, Progression, Input, Feedback
- Platformer: Movement, Physics, Camera, Level, Checkpoint, Enemy, Collectible
- Simulation: Simulation Rule, Economy, State, Time, AI, UI, Data Persistence
- Action: Controller, Combat, Enemy, Animation, Feedback, Level, Balancing

Roguelike와 Visual Novel에 같은 Workflow를 사용해서는 안 된다.

### 엔진별 기술

- Unity: C#, Input System, Scene, Prefab, ScriptableObject, Animator, Physics, Addressables, Profiler, Build Settings
- Unreal Engine: C++, Blueprint, Actor/Component, Gameplay Framework, Animation Blueprint, Niagara, Packaging
- Godot: GDScript/C#, Node/Scene, Signal, Resource, AnimationTree, Physics, Export Preset

엔진 컨텍스트는 사용법 전체가 아니라 시스템 구현에 필요한 기술, 선행 작업, 일반적인 위험을 알려주는 데 집중한다.

### 역할과 역량

- Gameplay Programmer: Engine, Programming, Physics, Debugging
- Game Designer: Core Loop, System Design, Level Design, Balancing, Documentation
- UI/UX Designer: Information Architecture, Layout, Interaction, Engine UI
- Artist/Animator: Art Pipeline, Asset Production, Animation, Engine Import
- Technical Artist: Shader, VFX, Art Pipeline, Optimization
- Scenario Writer: Narrative, Dialogue, Branching, Content Management
- QA: Test Design, Reproduction, Regression, Build Verification

### 태스크 의존성

```text
Player Controller → Combat System → Enemy Combat → Combat Balancing
Item Data Model → Inventory → Inventory UI → Save/Load
Dialogue Data Format → Dialogue Runtime → Choice Branching → Dialogue UI
```

태스크 생성 시 가능한 경우 dependency를 반드시 포함하고, 일정과 배정은 그 순서를 고려한다.

### 작업량 기준

고정 시간 하나보다 목표 수준별 시간 범위와 복잡도 보정값을 사용한다.

```json
{
  "system": "Inventory",
  "effort_hours": {
    "prototype": [6, 12],
    "mvp": [16, 30],
    "production": [40, 80]
  },
  "modifiers": {
    "multiplayer": 1.8,
    "drag_and_drop_ui": 1.3,
    "persistence": 1.2
  }
}
```

초기 추정치는 절대값으로 간주하지 않고 실제 프로젝트 결과가 쌓이면 보정한다.

## Dynamic Harness

Project Analyzer가 입력을 해석하면 Harness Config Builder가 다음 구성을 동적으로 선택한다.

- Context: Agent가 참고할 프로젝트·장르·엔진·기간·목표 지식
- Rules: 반드시 지켜야 하는 배정 및 범위 규칙
- Tools: 현재 프로젝트에 필요한 계산·검증 함수
- Workflow: 분석부터 검증까지의 실행 순서
- Role Candidates: 프로젝트에 필요한 역할 후보
- Validation Conditions: 결과가 충족해야 할 완료 조건
- Permissions: Agent가 읽거나 실행할 수 있는 범위

예를 들어 `Unity + 2D + Roguelike + 4명 + 4주 + MVP`에는 Unity, 2D, Roguelike, Small Team, Short Project, MVP Context가 선택된다. 반면 Visual Novel에는 Scenario, Dialogue, Branching, UI, Content Scale 중심의 Context와 Workflow가 선택된다.

## LLM과 일반 코드의 책임 경계

### LLM 또는 Planning Agent

- 자연어 프로젝트 설명 이해
- 핵심 게임 루프와 필요한 시스템 추론
- 프로젝트에 맞는 태스크 후보 생성
- 태스크별 요구 역량 추론
- 전체 배정안 판단과 근거 설명
- 사용자 수정 요청의 의도 해석

### Tools와 Validator

- Skill Match 점수 계산
- 작업량과 가용 시간 계산
- 일정 초과 검사
- 필수·중복·미배정 태스크 검사
- 존재하지 않는 팀원 검사
- 태스크 의존성과 순환 검사
- 역할 및 핵심 업무 편중 검사
- JSON Schema와 제약조건 검증
- 검증 실패 내용을 Agent에 전달

LLM의 주관적 판단만으로 점수, 시간, 제약 충족 여부를 결정하지 않는다. Agent가 만든 결과는 Validator를 통과한 뒤에만 사용자에게 반환하며, 실패하면 필수 태스크를 유지한 상태로 수정을 요청한다.

## 매칭 기준

개념적인 매칭 요소는 다음과 같다.

```text
Match Score = Skill + Experience + Preference + Availability + Learning Interest
```

- 핵심 기술과 경험을 가장 높은 비중으로 둔다.
- 가용 시간이 부족한 팀원에게 태스크를 배정하지 않는다.
- 선호 역할과 학습 관심사는 가산 요소다.
- 기피 역할은 강한 감점 또는 배정 금지 조건이다.
- 학습 목적이라도 핵심 시스템 전체를 경험이 없는 한 명에게 집중하지 않는다.
- 모든 배정에는 사람이 확인할 수 있는 근거가 있어야 한다.

가중치는 구현과 실제 사용 데이터를 바탕으로 조정하며 README의 개념식을 고정된 정책으로 간주하지 않는다.

## Structured Output

최종 응답에는 최소한 다음 데이터가 포함되어야 한다.

```json
{
  "project_analysis": {},
  "harness": {
    "contexts": [],
    "rules": [],
    "tools": [],
    "workflow": [],
    "role_candidates": [],
    "validation_conditions": []
  },
  "tasks": [],
  "assignments": [],
  "member_workload": [],
  "validation": {
    "valid": true,
    "errors": []
  }
}
```

프론트엔드는 프로젝트 분석, 카테고리별 태스크, 담당자별 역할·작업량, 태스크별 배정 근거, 검증 상태를 표시한다. 초기 결과는 확정안이 아니며 사용자가 자연어나 Form으로 제약을 추가해 재계산할 수 있다.

## 구성

- `gameweaver/`: 프로젝트 분석, Harness 구성, 태스크 생성, 매칭, 검증
- `web/`: 프로젝트/팀 입력과 분석 결과를 보여주는 단일 페이지 UI
- `app.py`: Python 표준 라이브러리 기반 API·정적 파일 서버
- `tests/`: 핵심 계획 및 검증 테스트
- `docs/architecture.md`: 책임 분리와 처리 흐름

## 실행

Python 3.11 이상만 필요합니다.

```powershell
Copy-Item .env.example .env
# .env의 OPENAI_API_KEY 값을 입력
python app.py
```

브라우저에서 `http://localhost:8000`을 엽니다.

## 명령어

- 실행: `python app.py`
- 테스트: `python -m unittest discover -s tests -v`
- 문법 검사: `python -m compileall app.py gameweaver tests`
- 외부 의존성: 없음

AI 계획을 사용하려면 `.env`에 `OPENAI_API_KEY`를 설정합니다. 모델은 기본적으로 `gpt-5.6-terra`이며 `OPENAI_MODEL`로 바꿀 수 있습니다. 키가 없거나 API 호출이 실패하면 규칙 기반 계획으로 자동 전환합니다. 구현은 OpenAI [Responses API](https://developers.openai.com/api/reference/cli/resources/responses/methods/create)와 strict JSON Schema Structured Outputs를 사용하며 API 응답 저장은 끕니다.

## API

- `GET /api/health`: 상태 확인
- `GET /api/projects`: 최근 계획 목록
- `GET /api/projects/{id}`: 저장된 입력과 계획 조회
- `POST /api/plan`: 프로젝트와 팀 정보를 분석해 계획 생성
- `POST /api/refine`: 기존 계획에 수정 제약조건을 적용해 재배정

예제 요청은 `examples/project.json`에 있습니다.

## MVP 범위

게임 프로젝트 입력, 팀원 입력, Dynamic Harness 구성, 장르별 태스크 생성, 스킬 매칭, 작업량 계산, 의존성/배정 검증, 배정 근거, 수정 요청을 지원합니다. GitHub/Jira/Slack/Calendar 연동, 실시간 관리, 장기 추적, Multi-Agent는 제외합니다.

## 현재 구현 상태

현재 버전은 외부 의존성 없이 Single Planning Agent와 규칙 기반 fallback을 모두 실행할 수 있는 MVP다.

- 완료: 확장된 프로젝트·팀원 Form, 외부 지식 기반 Harness, AI 태스크·핵심 루프 생성, 스킬 매칭, 배정, 작업량·일정 계산, 수정 요청, 결과 UI
- Planning Agent: OpenAI Responses API의 strict Structured Outputs 사용, Validator 오류를 전달해 최대 2회 자동 Retry
- 전용 데이터 보유: Roguelike, Visual Novel, RPG, Puzzle, Platformer, Simulation, Action
- 엔진 데이터 보유: Unity, Unreal Engine, Godot
- 저장: 프로젝트 입력, 생성 결과와 수정 이력을 로컬 SQLite에 저장하고 최근 계획 조회
- 검증 완료: 결과 구조, 필수·중복·미배정 태스크, 존재하지 않는 팀원, 작업량 초과, dependency 누락·순환, 일정 초과, 70% 초과 업무 편중
- 후속 개선: 실제 프로젝트 데이터에 따른 작업 시간·매칭 가중치 보정, 인증과 사용자별 저장소, 운영 환경 배포

도메인 지식은 아래 `knowledge/` 구조로 분리한다. 현재 공통 규칙·역할, Roguelike, Visual Novel, Unity, Unreal Engine, Godot 데이터가 구성되어 있다.

```text
knowledge/
├── common/
│   ├── development-phases.json
│   ├── roles.json
│   └── validation-rules.json
├── genres/
│   ├── roguelike.json
│   ├── visual-novel.json
│   ├── rpg.json
│   └── puzzle.json
├── engines/
│   ├── unity.json
│   ├── unreal.json
│   └── godot.json
└── platforms/
    ├── pc.json
    ├── mobile.json
    └── web.json
```

각 시스템 지식은 적용 조건, 태스크, 요구 역량, 의존성, 목표별 작업량 범위와 검증 규칙을 가져야 한다.

```json
{
  "system": "Inventory",
  "applies_when": ["RPG", "Roguelike"],
  "tasks": ["Item Data Model", "Inventory Logic", "Inventory UI"],
  "required_skills": {"Programming": 3, "UI": 2},
  "dependencies": ["Item Data Model"],
  "effort_hours": {"prototype": [6, 12], "mvp": [16, 30]},
  "validation": ["Save strategy must be defined"]
}
```

## 초기 버전에서 제외하는 기능

- GitHub, Jira, Slack, Discord, Google Calendar 연동
- 실시간 프로젝트 관리와 장기간 작업 추적
- 자동 배포 및 외부 서비스 변경
- Multi-Agent

이 기능들은 Single Agent와 Dynamic Harness의 품질이 검증된 뒤 필요성이 확인될 때 추가한다.
