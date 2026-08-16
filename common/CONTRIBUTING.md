# Git 협업 규칙

## 브랜치 규칙

| 브랜치 | 용도 |
| --- | --- |
| `main` | 최종 발표 및 배포 가능한 안정 버전 |
| `develop` | 기능을 통합하고 테스트하는 개발 버전 |
| `feature/*` | 개별 기능 개발 |
| `hotfix/*` | 발표 또는 배포 직전의 긴급 수정 |

`main`과 `develop`에는 직접 커밋하지 않고 Pull Request로 반영합니다.

### 일반 작업 흐름

1. 열린 이슈에서 같은 작업을 찾고, 없으면 기능 또는 버그 이슈를 생성합니다.
2. `develop`에서 `feature/<issue-number>-<short-name>` 브랜치를 생성합니다.
3. 기능을 개발하고 관련 검사를 실행합니다.
4. `feature/*`에서 `develop`을 대상으로 Pull Request를 생성하고 `Refs #<issue-number>`를 작성합니다.
5. `develop`에서 통합 테스트를 진행합니다.
6. 발표 또는 배포 가능한 시점에 `develop`에서 `main`으로 Pull Request를 생성하고 `Closes #<issue-number>`를 작성합니다.
7. `main`에는 안정 버전만 유지합니다.

```text
main
└── develop
    ├── feature/12-frontend-init
    ├── feature/13-backend-auth
    ├── feature/14-wiki-crud
    ├── feature/15-rag-chatbot
    └── feature/16-docs-erd
```

### 긴급 수정 흐름

1. 관련 버그 이슈를 찾거나 생성합니다.
2. `main`에서 `hotfix/<issue-number>-<short-name>` 브랜치를 생성합니다.
3. 수정과 검증 후 `main`을 대상으로 Pull Request를 생성하고 `Closes #<issue-number>`를 작성합니다.
4. 완료된 수정사항을 `develop`에도 반영합니다.

## 커밋 규칙

형식은 `<type>: <subject>`입니다. 콜론 뒤에 공백을 한 칸 넣고, subject에는 변경 내용을 간결하게 작성합니다.

| Type | 용도 |
| --- | --- |
| `feat` | 새로운 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 수정 |
| `style` | 동작 변화 없는 코드 포매팅 및 스타일 변경 |
| `design` | 사용자 UI 변경 |
| `test` | 테스트 코드 추가 및 수정 |
| `refactor` | 동작 변화 없는 리팩터링 |
| `chore` | 설정 등 자잘한 수정 |
| `rename` | 파일 또는 폴더 이름 변경 |
| `remove` | 파일 또는 코드를 삭제만 한 경우 |

예시:

```text
feat: 사용자 로그인 기능 추가

Refs #12
```

이슈 하나는 기능 또는 버그 하나를 추적합니다. 푸시나 커밋마다 새 이슈를 만들지 않습니다.

```text
fix: 빈 문서 저장 오류 수정
docs: API 명세 갱신
```

## Pull Request 규칙

제목은 `[PR type] 주요 기능` 형식으로 작성합니다.

| PR type | 용도 |
| --- | --- |
| `[기능 추가]` | 신규 기능 추가 |
| `[버그 수정]` | 버그 수정 |
| `[배포 수정]` | 배포 관련 수정 |

본문에는 다음 내용을 포함합니다.

- 추가하거나 수정한 기능명
- 관련 이슈 번호 (`develop` 대상은 `Refs #123`, `main` 대상은 `Closes #123`)
- 어느 코드를 어떤 방식으로 수정했는지
- 테스트, 빌드 또는 실행 결과

## Issue 규칙

제목은 `[Issue type] 주요 내용` 형식으로 작성합니다.

| Issue type | 용도 |
| --- | --- |
| `[기능 요청]` | 신규 기능 추가 요청 |
| `[버그]` | 기존 기능의 버그 제보 |

본문에는 이슈 내용, 발생한 문제, 재현 방법과 관련 코드 또는 로그를 가능한 한 자세히 작성합니다. 비밀정보와 개인정보는 제거합니다.

작업 시작 전에 열린 이슈를 검색합니다. 같은 기능이나 버그가 있으면 기존 이슈를 사용하고, 없을 때만 새 이슈를 생성합니다. 구현 요약과 검증 결과는 Pull Request에 기록하며, 의미 있는 결정이나 장애가 아닌 푸시별 진행 댓글은 남기지 않습니다.

예시:

```text
[기능 요청] 프로젝트 초기 구조 생성
[기능 요청] 프론트엔드 React 초기 설정
[기능 요청] 백엔드 Spring Boot 초기 설정
[기능 요청] AI RAG 서버 초기 설정
[기능 요청] ERD 및 API 명세 작성
```
