![환마 귀무자 한국어 타이틀 화면](docs/images/title.png)

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

MD5·SHA-1·SHA-256과 패처 해시는 [HASHES-v0.801.md](HASHES-v0.801.md), [SHA256SUMS.txt](SHA256SUMS.txt)에 있습니다. 패처는 적용 전후 SHA-256을 자동 확인합니다.

## 한글화 범위

- 게임 대사, 조사문, 아이템 이름과 설명, 획득 메시지
- 타이틀·설정·조작·저장·불러오기·지도·강화·결과 화면
- 일반 문서와 지침서, 암호책의 설명, 이미지에 들어간 메뉴와 랭크
- 영상 자막, 오프닝 편지 낭독 자막, 크레딧

궁서·붓글씨 계열로 게임 분위기를 맞췄습니다. 문서 읽기 방향과 종이 안쪽 여백, 메뉴 정렬, 선택지 간격, 숫자와 작은 글자의 가독성을 보수했습니다. 암호 퍼즐의 원래 문자와 수집 조건은 유지합니다. 오프닝 편지의 일본어 원화는 유지하고 음성에 맞춘 가로 한국어 자막을 표시합니다.

v0.8에는 내부 검수본 r16까지의 수정 사항을 담았습니다. 최신 텍스트 재검수에서 조사문 의미와 관찰 표현, 인물 말투 5행을 보완했으며, 확대 글꼴 처리 중 원본 범위를 벗어나는 읽기를 막는 수정도 포함합니다.

## v0.801 변경 내용과 검사

v0.8의 전체 한글화 데이터와 검증된 v0.801 수정 XBE를 통합했습니다. 원본의 23개 섹션 구조와 기존 헤더·이름·참조 포인터 배치를 사용하고, HDD 매체 허용과 파일 끝 정렬을 보정했습니다. 한글 처리 코드·문자열·자막과 원본 타이틀 아이콘은 유지합니다. ISO 내부 XBE 역시 한글 코드가 들어간 수정 실행 파일입니다.

- 배포 Windows EXE에 일본판 원본 ISO를 실제로 입력하여 전체 결과 ISO를 생성하고, 독립 SHA-256 검사까지 통과했습니다.
- ISO의 1,820개 디렉터리 항목(파일 1,743개)을 검사했습니다. v0.8 대비 XBE 위치 정보와 추가된 수정 XBE 외의 기존 바이트는 모두 동일합니다.
- 결과 ISO 내부 XBE가 기존 네이티브 검사 5,219조건을 통과한 파일과 바이트 단위로 일치합니다. 본문 3,768페이지, 글리프·메뉴·저장·선택지·문서·영상·크레딧 12종 검사 기록이 있습니다.
- 원본 보존, 기존 출력 보존, 잘못된 원본·경로·확장자 및 중복 패치 입력 거부를 검사했습니다. 실제 ISO 생성 도중 취소한 뒤 미완성 출력이 정리되는 것도 확인했습니다.

**실기 Xbox 부팅과 전체 플레이는 미검증입니다.** 데이터와 CPU 출력 검사 결과를 구분하여 공개하는 테스트 릴리스입니다. 제보된 실기 부팅 문제가 해결되었다고 확정하지 않습니다.

## 스크린샷

기존 개발 중 확보한 에뮬레이터 캡처이며, v0.801 실기 실행 캡처는 아닙니다.

![한국어 대사](docs/images/dialogue.png)

![오프닝 한국어 자막](docs/images/opening-caption.png)

## 검수 기록

노부나가의 오프닝 구호와 영상의 짧은 응답 2구간은 청취 미확정입니다. 원본 특수 방별 선택 분기 7행은 완전히 재현하지 못했습니다.

- [통합 패처 실제 적용과 전체 ISO 검증](docs/verification/patcher-v0.801.json)
- [수정 XBE 네이티브 출력 검사](docs/verification/hdd-text-fix.json)
- [텍스트 재검수](docs/TEXT_REVIEW.md)
- [기본 한글판 실기 호환성 데이터 검사](docs/HARDWARE_DATA_AUDIT.md)

## 패처 소스 재빌드

유지보수용 통합 이미지 조립 도구는 로컬 일본판 원본 ISO와 v0.8 ISO에서 동일한 v0.801 ISO를 만듭니다. 일반 사용자는 위 Windows 패처만 실행하면 됩니다.

```powershell
python tools/build_integrated_iso.py --original-iso "일본판 원본.iso" --base-iso "v0.8 결과.iso" --output "통합 v0.801.iso"
python tools/make_patch.py --source "일본판 원본.iso" --target "통합 v0.801.iso" --xdelta "xdelta3.exe"
python tools/package_release.py --source "일본판 원본.iso" --target "통합 v0.801.iso" --decoder "xdelta3.exe"
python tools/verify_release.py --source "일본판 원본.iso" --base-v08 "v0.8 결과.iso" --output "검증 v0.801.iso"
```

패키징은 Python 3.11 이상과 Windows .NET Framework C# 컴파일러를 사용합니다. [Xdelta 3.2.1](https://github.com/jmacd/xdelta/releases/tag/v3.2.1)의 LZMA 지원 Windows x86-64 `xdelta3.exe`가 필요합니다. 게임 자료와 완성 ISO는 저장소에 포함하지 않습니다. 외부 구성 요소의 출처와 라이선스는 [licenses](licenses/THIRD-PARTY.md)에 있습니다. 게임과 원본 그래픽의 권리는 각 권리자에게 있습니다.
