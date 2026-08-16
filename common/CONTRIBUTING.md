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

1. `develop`에서 `feature/<short-name>` 브랜치를 생성합니다.
2. 기능을 개발하고 관련 검사를 실행합니다.
3. `feature/*`에서 `develop`을 대상으로 Pull Request를 생성합니다.
4. `develop`에서 통합 테스트를 진행합니다.
5. 발표 또는 배포 가능한 시점에 `develop`에서 `main`으로 Pull Request를 생성합니다.
6. `main`에는 안정 버전만 유지합니다.

```text
main
└── develop
    ├── feature/frontend-init
    ├── feature/backend-auth
    ├── feature/wiki-crud
    ├── feature/rag-chatbot
    └── feature/docs-erd
```

### 긴급 수정 흐름

1. `main`에서 `hotfix/<short-name>` 브랜치를 생성합니다.
2. 수정과 검증 후 `main`을 대상으로 Pull Request를 생성합니다.
3. 완료된 수정사항을 `develop`에도 반영합니다.

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
- 관련 이슈가 있다면 이슈 번호
- 어느 코드를 어떤 방식으로 수정했는지
- 테스트, 빌드 또는 실행 결과

## Issue 규칙

제목은 `[Issue type] 주요 내용` 형식으로 작성합니다.

| Issue type | 용도 |
| --- | --- |
| `[기능 요청]` | 신규 기능 추가 요청 |
| `[버그]` | 기존 기능의 버그 제보 |

본문에는 이슈 내용, 발생한 문제, 재현 방법과 관련 코드 또는 로그를 가능한 한 자세히 작성합니다. 비밀정보와 개인정보는 제거합니다.

예시:

```text
[기능 요청] 프로젝트 초기 구조 생성
[기능 요청] 프론트엔드 React 초기 설정
[기능 요청] 백엔드 Spring Boot 초기 설정
[기능 요청] AI RAG 서버 초기 설정
[기능 요청] ERD 및 API 명세 작성
```
