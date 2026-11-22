"""Write versioned release notes after the packaged EXE has passed verification."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr'


def main():
    m = json.loads((ROOT / 'release-manifest.json').read_text('utf8'))
    v = m['version']; raw = REPO.replace('github.com/', 'raw.githubusercontent.com/') + '/' + v
    proof = json.loads((ROOT / f'docs/verification/patcher-{v}.json').read_text('utf8'))
    extra = json.loads((ROOT / f'docs/verification/patcher-extra-{v}.json').read_text('utf8'))
    assert m['windows_exe_roundtrip_verified'] and proof['status'] == extra['status'] == 'passed'
    assert proof['patcher_sha256'] == extra['patcher_sha256'] == m['patcher']['sha256']
    notes = f'''![환마 귀무자 {v} 실제 타이틀 화면]({raw}/docs/images/title-{v}.png)

# 환마 귀무자 한국어 패치 {v} · 단일 ISO

**한글화: 기타 깎는 노인**

**일본판 원본 ISO에서 전체 한글화를 포함한 ISO 한 파일을 생성합니다.** 수정 default.xbe와 한글 데이터가 ISO 안에 포함되어 있으며, 한글화용 별도 로더·RAM 패처·플러그인·외부 설정 파일은 필요 없습니다. 기존 구엑박 게임 실행 환경과 일반적인 설치 절차는 필요합니다.

맨 위는 **최종 {v} 파일을 실행한 PC Cxbx Retail 모드의 실제 타이틀 캡처**입니다. **Xbox 360/XeFu와 실기 Xbox 실행은 미검증**입니다. 기존 실행 불가 제보를 해결했다고 확정한 배포물은 아니며, 이 한계를 표시한 사전 배포판입니다.

## 다운로드·적용

1. 아래 Assets에서 **`XBOX-Genma-Onimusha-Kr-{v}-Windows-Patcher.zip`**을 받고 압축을 풉니다. 단독 **Patcher.exe**도 같은 기능입니다.
2. **`Genma Onimusha (Japan) (En,Ja)` 일본판 원본 ISO**와 새 ISO 저장 위치를 선택합니다.
3. **한글 패치 시작**을 누르고 결과 ISO 및 내부 XBE 해시 검증이 끝날 때까지 기다립니다.
4. 게임 문자 언어는 **日本語(일본어)**로 두세요. 음성 설정은 별개입니다.

Windows 10/11 64비트용이며 Python 설치는 필요 없습니다. 출력 드라이브 6GB 이상, 임시 폴더 200MB 이상의 빈 공간이 필요합니다. 원본·기존 출력은 덮어쓰지 않습니다. 이전 한글 패치나 XBE 수동 교체 없이 **일본판 원본부터 적용**하세요.

결과는 4GB가 넘는 XDVDFS ISO입니다. NTFS/exFAT에 저장하고, Xbox/360의 기존 설치 방식에 맞게 일반적인 추출·변환 절차를 진행하세요. 5GB ISO 한 파일을 FATX에 그대로 복사할 수 있다는 뜻은 아닙니다. **게임 원본과 완성 ISO는 배포하지 않습니다.**

## 이번 버전

- v0.802에서 일본어로 남겼던 **메뉴·아이템명·설명·선택지 327행**의 한글 처리를 포함합니다.
- 대사·조사문·시스템 메시지, 본문 **3,768페이지**, 문서·지침서·암호책 풀이와 이미지 UI를 포함합니다. 암호 기호·문서 해금·풀이 순서는 유지합니다.
- 오프닝을 포함한 영상의 **시간 지정 자막 86개**와 한글 크레딧을 포함합니다. 전체 영상 끝까지의 재생 검증은 별개입니다.
- 인게임 자막 가운데 정렬, 획득 문구 두 줄 배치, 선택지 간격, 문서의 종이 영역, 지도 제목 가운데 정렬, 시작 버튼 안내의 아래 이동을 반영합니다.
- 랭크·조작·저장 화면과 암호책 탭·버튼을 보수한 전체 한글 리소스를 사용합니다.
- 같은 자막 이미지 20건을 공유해 **추가 선행 로드 메모리를 143,360바이트 절약**했습니다. 기존 전체 한글판과 글자·좌표는 같습니다.

v0.803은 로컬 비교 후보였으며 공개판이 아닙니다. 이번 판은 XBE 무수정판이 아닙니다.

## 일본판 형태 보존

원본 23개 섹션의 주소·길이·플래그·섹션 표 시작 위치, 진입점, 커널 참조 116개, TLS·시작 스택/힙 설정과 **인증서 전체·지역 0x2·허용 매체 0x2**를 유지합니다.

한글 처리용 **KRDATA 섹션 1개**를 추가하고, 원본 .text 206바이트·.data 1,225바이트 및 관련 헤더·해시를 변경했습니다. 그 외 원본 21개 섹션 내용은 같습니다. XBE 전체가 원본과 같은 것은 아니며, 실행 환경이 수정 XBE를 허용해야 합니다. 파일·디렉터리 이름은 일본판과 같지만, 커진 번역 데이터의 ISO 위치까지 모두 일본판과 같지는 않습니다.

## 확인한 내용과 남은 검증

- 12개 검사 모듈 통과, 실제 x86 글자 배치 **5,219건** 일치, CPU 검사 이미지 9장 및 실제 GPU 타이틀 화면의 픽셀 일치.
- 읽기·실행 전용 추가 공간에서 **7,917회** 실행, 텍스처 변환·스위즐 8건, 컨테이너 복사 239건 검사.
- 최종 게임 파일 1,743개로 **PC Cxbx Retail 모드 초기화·영상 프레임 진행·타이틀 진입** 확인.
- 기존 전체 한글 r16 대비 XBE 할당 영역·길이 필드 외 예상 밖 ISO 변경 **0바이트**. XBE의 불필요한 끝부분 143,360바이트 정리.
- **배포 EXE로 원본에서 전체 ISO를 다시 생성**, 결과 SHA-256·내부 XBE·원본 인증서·파일 목록 확인. 잘못된 입력 거부·기존 파일 보존·생성 중 취소·미완성 출력 정리 검사.

**Xbox 360/XeFu 부팅, 실기 Xbox 부팅, 전체 플레이, 모든 영상 전체 재생, 64MB 환경 전체 구간 최대 메모리 사용량은 미검증입니다.** PC 에뮬레이터 결과로 360 실행을 보장하지 않습니다.

## 해시

| 대상 | 크기 (bytes) | SHA-256 |
| --- | ---: | --- |
| 일본판 원본 ISO | {m['source']['bytes']:,} | `{m['source']['sha256']}` |
| {v} 결과 ISO | {m['output']['bytes']:,} | `{m['output']['sha256']}` |
| ISO 내부 수정 default.xbe | {m['integrated_default_xbe']['bytes']:,} | `{m['integrated_default_xbe']['sha256']}` |
| Windows Patcher.exe | {m['patcher']['bytes']:,} | `{m['patcher']['sha256']}` |

[MD5·SHA-1·SHA-256 전체 목록]({REPO}/blob/{v}/HASHES-{v}.md) · [검사 결과와 사용법]({REPO}/tree/{v})

## 한글 배치 검사 이미지

아래는 원본 x86 글자 배치 결과로 만든 **CPU 검사 이미지**입니다. 에뮬레이터·실기 실행 캡처가 아닙니다.

![메뉴·아이템·선택지 한글 배치]({raw}/docs/verification/{v}/ui-proof.png)

![인게임 대사 한글 배치]({raw}/docs/verification/{v}/dialogue-proof.png)
'''
    for p in (ROOT / 'RELEASE_NOTES.md', ROOT / 'docs/releases' / (v + '.md')):
        p.write_text(notes, 'utf8')
    print(f'Wrote verified {v} release notes')


if __name__ == '__main__':
    main()
