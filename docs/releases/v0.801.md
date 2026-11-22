![환마 귀무자 한국어 타이틀 화면](https://raw.githubusercontent.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr/main/docs/images/title.png)

# XBOX-Genma-Onimusha-Kr · v0.801

Xbox용 **환마 귀무자 (Genma Onimusha)** 일본판 한국어 패치입니다.

**한글화: 기타 깎는 노인**

**일본판 원본 ISO → v0.801 통합 한글 ISO 한 파일**로 바로 생성합니다. 한글 코드와 수정 XBE가 ISO 내부에 포함됩니다. v0.8 선행 적용이나 XBE 수동 교체는 필요 없습니다.

## 다운로드와 적용

1. [v0.801 릴리스](https://github.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr/releases/tag/v0.801)에서 **`XBOX-Genma-Onimusha-Kr-v0.801-Windows-Patcher.zip`**을 내려받고 압축을 풉니다.
2. `XBOX-Genma-Onimusha-Kr-v0.801-Patcher.exe`를 실행합니다. 단독 EXE도 같은 기능을 제공합니다.
3. **`Genma Onimusha (Japan) (En,Ja)` 일본판 원본 ISO**를 선택합니다.
4. 새 ISO 저장 위치를 지정하고 **한글 패치 시작**을 누릅니다.
5. 결과 ISO SHA-256 검증과 완료 메시지를 기다립니다. 완성되는 결과물은 **ISO 한 파일**입니다.

기존 v0.8 사용자도 일본판 원본 ISO에서 새로 생성하세요. 기존 한글 ISO에 중복 적용하지 않습니다. 앞서 배포했던 XBE 교체용 v0.801 ZIP은 이 통합 패처로 대체했습니다.

Windows 10/11 64비트용이며 Python 설치가 필요 없습니다. 출력 위치에 **6GB 이상**, 임시 폴더에 **200MB 이상**의 빈 공간이 필요합니다. 결과 ISO는 4GB를 넘으므로 NTFS 또는 exFAT에 저장하세요. 원본과 기존 출력 파일은 덮어쓰지 않습니다.

게임 원본 ISO는 포함하지 않습니다. 다른 지역판·다른 추출 형식·이미 패치된 ISO는 지원하지 않습니다. 출력은 원본과 같은 XDVDFS 게임 이미지이며, 설치용 추출·변환은 사용하는 로더의 형식에 맞게 진행하세요.

### 지원 원본과 결과

| 대상 | 크기 (bytes) | SHA-256 |
| --- | ---: | --- |
| 일본판 원본 ISO | 4,905,566,208 | `7f5af784f9b229c5d0061918e018a9052e328a5341efc7d9e1b5d36de5f58206` |
| v0.801 통합 결과 ISO | 5,388,861,440 | `189e10e695429dc212a70efc6f31a9dfdc41a18c50ecccad90d735d1a2a0468e` |

MD5·SHA-1·SHA-256과 패처 해시는 [HASHES-v0.801.md](https://github.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr/blob/main/HASHES-v0.801.md), [SHA256SUMS.txt](https://github.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr/blob/main/SHA256SUMS.txt)에 있습니다. 패처는 적용 전후 SHA-256을 자동 확인합니다.

## v0.801 변경 내용과 검사

v0.8의 전체 한글화 데이터와 검증된 v0.801 수정 XBE를 통합했습니다. 원본의 23개 섹션 구조와 기존 헤더·이름·참조 포인터 배치를 사용하고, HDD 매체 허용과 파일 끝 정렬을 보정했습니다. 한글 처리 코드·문자열·자막과 원본 타이틀 아이콘은 유지합니다. ISO 내부 XBE 역시 한글 코드가 들어간 수정 실행 파일입니다.

- 배포 Windows EXE에 일본판 원본 ISO를 실제로 입력하여 전체 결과 ISO를 생성하고, 독립 SHA-256 검사까지 통과했습니다.
- ISO의 1,820개 디렉터리 항목(파일 1,743개)을 검사했습니다. v0.8 대비 XBE 위치 정보와 추가된 수정 XBE 외의 기존 바이트는 모두 동일합니다.
- 결과 ISO 내부 XBE가 기존 네이티브 검사 5,219조건을 통과한 파일과 바이트 단위로 일치합니다. 본문 3,768페이지, 글리프·메뉴·저장·선택지·문서·영상·크레딧 12종 검사 기록이 있습니다.
- 원본 보존, 기존 출력 보존, 잘못된 원본·경로·확장자 및 중복 패치 입력 거부를 검사했습니다. 실제 ISO 생성 도중 취소한 뒤 미완성 출력이 정리되는 것도 확인했습니다.

**실기 Xbox 부팅과 전체 플레이는 미검증입니다.** 데이터와 CPU 출력 검사 결과를 구분하여 공개하는 테스트 릴리스입니다. 제보된 실기 부팅 문제가 해결되었다고 확정하지 않습니다.

## 스크린샷

기존 개발 중 확보한 에뮬레이터 캡처이며, v0.801 실기 실행 캡처는 아닙니다.

![한국어 대사](https://raw.githubusercontent.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr/main/docs/images/dialogue.png)

![오프닝 한국어 자막](https://raw.githubusercontent.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr/main/docs/images/opening-caption.png)

## 검수 기록

노부나가의 오프닝 구호와 영상의 짧은 응답 2구간은 청취 미확정입니다. 원본 특수 방별 선택 분기 7행은 완전히 재현하지 못했습니다.

- [통합 패처 실제 적용과 전체 ISO 검증](https://github.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr/blob/main/docs/verification/patcher-v0.801.json)
- [수정 XBE 네이티브 출력 검사](https://github.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr/blob/main/docs/verification/hdd-text-fix.json)
- [텍스트 재검수](https://github.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr/blob/main/docs/TEXT_REVIEW.md)
- [기본 한글판 실기 호환성 데이터 검사](https://github.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr/blob/main/docs/HARDWARE_DATA_AUDIT.md)


2026-11-22: XBE 교체용 배포를 일본판 원본용 통합 ISO 패처로 변경했습니다. 기존 v0.801 태그는 유지하며, 갱신된 패처 소스와 검증 기록은 main 브랜치에 있습니다.
