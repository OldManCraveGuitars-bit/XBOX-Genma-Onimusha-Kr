# v0.804 검사 자료

이 폴더의 JSON은 GitHub 게시 전에 수행한 로컬 데이터·PC 실행 검사의 원본 기록입니다. 기록에 있는 `github_publication_allowed: false`는 해당 검사 당시의 조건이며, 이후 사용자의 게시 요청을 반영한 릴리스 상태를 나타내는 필드는 아닙니다.

- `build.json`: XBE 빌드 직후 기록. 당시 상태는 `built_pending_quality_review`이며, 이후 검사 결과는 다음 자료에 있습니다.
- `quality.json`: 12개 모듈·글자 배치·픽셀 비교 검사 통과.
- `retail_parity.json`: 일본판 원본의 섹션 배치·시작 설정·인증서와 비교.
- `iso.json`: 최종 ISO 전체 검사. 출력 경로는 로컬 빌드 경로이며, 배포 패처의 결과 파일 이름과 달라도 내용 해시는 같습니다.
- `boot.json`: 최종 XBE를 사용한 PC Cxbx Retail 모드의 영상 진행·타이틀 진입 확인.
- `ui-proof.png`, `dialogue-proof.png`: CPU 글자 배치 검사 이미지. 실기 또는 에뮬레이터 화면 캡처가 아닙니다.

배포 EXE를 실제 적용한 결과는 상위 폴더의 [patcher-v0.804.json](../patcher-v0.804.json), 취소와 패처 창 범위 검사는 [patcher-extra-v0.804.json](../patcher-extra-v0.804.json)에 있습니다.

**Xbox 360/XeFu 및 실기 Xbox 부팅은 미검증입니다.**
