# Workflows

기술 스택별 CI는 각 프로젝트에서 실제 실행 가능한 명령으로 추가합니다.

## Notion commit log

`notion-commit-log.yml`은 `main` 또는 `develop`에 푸시된 커밋을 Notion에 기록합니다.

저장소 설정에 다음 값을 등록해야 합니다.

- Actions secret `NOTION_TOKEN`: 대상 데이터 소스에 콘텐츠 추가 권한이 있는 Notion Integration 토큰
- Actions variable `NOTION_DATA_SOURCE_ID`: Notion 데이터 소스 ID

Notion Integration에 대상 데이터베이스를 공유하지 않으면 API 요청이 실패합니다.

설정 후 `main` 또는 `develop`에 커밋을 푸시하고, Actions 실행 성공과 Notion 항목 생성을 함께 확인합니다.
