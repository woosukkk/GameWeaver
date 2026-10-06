# Scripts

반복적인 수동 복사가 불편해질 때 최소한의 프로젝트 초기화 스크립트를 추가합니다.

## GitHub 이슈 메타데이터 갱신

`python scripts/refresh_github_issues.py`는 OpenRA, OpenTTD, SuperTuxKart의 최근 공개 이슈에서 제목, 라벨, 상태, 링크만 수집합니다. 이슈 본문은 복제하지 않습니다. 익명 API 제한을 피하려면 선택적으로 `GITHUB_TOKEN`을 설정합니다.
