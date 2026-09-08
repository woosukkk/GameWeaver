# GameWeaver

Dynamic Harness 기반 게임 개발 태스크·인력 배분 MVP입니다. 프로젝트 특성에 맞춰 Context, Rule, Tool, Workflow를 구성하고, 계산 가능한 항목은 코드로 점수화·검증합니다.

## 구성

- `gameweaver/`: 프로젝트 분석, Harness 구성, 태스크 생성, 매칭, 검증
- `web/`: 프로젝트/팀 입력과 분석 결과를 보여주는 단일 페이지 UI
- `app.py`: Python 표준 라이브러리 기반 API·정적 파일 서버
- `tests/`: 핵심 계획 및 검증 테스트
- `docs/architecture.md`: 책임 분리와 처리 흐름

## 실행

Python 3.11 이상만 필요합니다.

```powershell
python app.py
```

브라우저에서 `http://localhost:8000`을 엽니다.

## 명령어

- 실행: `python app.py`
- 테스트: `python -m unittest discover -s tests -v`
- 문법 검사: `python -m compileall app.py gameweaver tests`
- 외부 의존성: 없음

## API

- `GET /api/health`: 상태 확인
- `POST /api/plan`: 프로젝트와 팀 정보를 분석해 계획 생성
- `POST /api/refine`: 기존 계획에 수정 제약조건을 적용해 재배정

예제 요청은 `examples/project.json`에 있습니다.

## MVP 범위

게임 프로젝트 입력, 팀원 입력, Dynamic Harness 구성, 장르별 태스크 생성, 스킬 매칭, 작업량 계산, 의존성/배정 검증, 배정 근거, 수정 요청을 지원합니다. GitHub/Jira/Slack/Calendar 연동, 실시간 관리, 장기 추적, Multi-Agent는 제외합니다.
