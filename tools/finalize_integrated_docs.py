"""Write the integrated v0.801 download instructions after EXE verification."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr'


def main():
    m = json.loads((ROOT / 'release-manifest-v0.801.json').read_text('utf8'))
    assert m['windows_exe_roundtrip_verified'] and m['iso_content_audit_verified']
    source, output = m['source'], m['output']
    archive = next(a['name'] for a in m['assets'] if a['name'].endswith('-Windows-Patcher.zip'))
    head = '''![환마 귀무자 한국어 타이틀 화면](docs/images/title.png)

# XBOX-Genma-Onimusha-Kr · v0.801

Xbox용 **환마 귀무자 (Genma Onimusha)** 일본판 한국어 패치입니다.

**한글화: 기타 깎는 노인**

**일본판 원본 ISO → v0.801 통합 한글 ISO 한 파일**로 바로 생성합니다. 한글 코드와 수정 XBE가 ISO 내부에 포함됩니다. v0.8 선행 적용이나 XBE 수동 교체는 필요 없습니다.

'''
    instructions = f'''## 다운로드와 적용

1. [v0.801 릴리스]({REPO}/releases/tag/v0.801)에서 **`{archive}`**을 내려받고 압축을 풉니다.
2. `{m['patcher']['name']}`를 실행합니다. 단독 EXE도 같은 기능을 제공합니다.
3. **`Genma Onimusha (Japan) (En,Ja)` 일본판 원본 ISO**를 선택합니다.
4. 새 ISO 저장 위치를 지정하고 **한글 패치 시작**을 누릅니다.
5. 결과 ISO SHA-256 검증과 완료 메시지를 기다립니다. 완성되는 결과물은 **ISO 한 파일**입니다.

기존 v0.8 사용자도 일본판 원본 ISO에서 새로 생성하세요. 기존 한글 ISO에 중복 적용하지 않습니다. 앞서 배포했던 XBE 교체용 v0.801 ZIP은 이 통합 패처로 대체했습니다.

Windows 10/11 64비트용이며 Python 설치가 필요 없습니다. 출력 위치에 **6GB 이상**, 임시 폴더에 **200MB 이상**의 빈 공간이 필요합니다. 결과 ISO는 4GB를 넘으므로 NTFS 또는 exFAT에 저장하세요. 원본과 기존 출력 파일은 덮어쓰지 않습니다.

게임 원본 ISO는 포함하지 않습니다. 다른 지역판·다른 추출 형식·이미 패치된 ISO는 지원하지 않습니다. 출력은 원본과 같은 XDVDFS 게임 이미지이며, 설치용 추출·변환은 사용하는 로더의 형식에 맞게 진행하세요.

### 지원 원본과 결과

| 대상 | 크기 (bytes) | SHA-256 |
| --- | ---: | --- |
| 일본판 원본 ISO | {source['bytes']:,} | `{source['sha256']}` |
| v0.801 통합 결과 ISO | {output['bytes']:,} | `{output['sha256']}` |

MD5·SHA-1·SHA-256과 패처 해시는 [HASHES-v0.801.md](HASHES-v0.801.md), [SHA256SUMS.txt](SHA256SUMS.txt)에 있습니다. 패처는 적용 전후 SHA-256을 자동 확인합니다.

'''
    changes = '''## v0.801 변경 내용과 검사

v0.8의 전체 한글화 데이터와 검증된 v0.801 수정 XBE를 통합했습니다. 원본의 23개 섹션 구조와 기존 헤더·이름·참조 포인터 배치를 사용하고, HDD 매체 허용과 파일 끝 정렬을 보정했습니다. 한글 처리 코드·문자열·자막과 원본 타이틀 아이콘은 유지합니다. ISO 내부 XBE 역시 한글 코드가 들어간 수정 실행 파일입니다.

- 배포 Windows EXE에 일본판 원본 ISO를 실제로 입력하여 전체 결과 ISO를 생성하고, 독립 SHA-256 검사까지 통과했습니다.
- ISO의 1,820개 디렉터리 항목(파일 1,743개)을 검사했습니다. v0.8 대비 XBE 위치 정보와 추가된 수정 XBE 외의 기존 바이트는 모두 동일합니다.
- 결과 ISO 내부 XBE가 기존 네이티브 검사 5,219조건을 통과한 파일과 바이트 단위로 일치합니다. 본문 3,768페이지, 글리프·메뉴·저장·선택지·문서·영상·크레딧 12종 검사 기록이 있습니다.
- 원본 보존, 기존 출력 보존, 잘못된 원본·경로·확장자 및 중복 패치 입력 거부를 검사했습니다. 실제 ISO 생성 도중 취소한 뒤 미완성 출력이 정리되는 것도 확인했습니다.

**실기 Xbox 부팅과 전체 플레이는 미검증입니다.** 데이터와 CPU 출력 검사 결과를 구분하여 공개하는 테스트 릴리스입니다. 제보된 실기 부팅 문제가 해결되었다고 확정하지 않습니다.

'''
    old = (ROOT / 'README.md').read_text('utf8')
    start = old.index('## 한글화 범위')
    scope = old[start:old.index('\n## ', start + 1) + 1]
    screenshots = '''## 스크린샷

기존 개발 중 확보한 에뮬레이터 캡처이며, v0.801 실기 실행 캡처는 아닙니다.

![한국어 대사](docs/images/dialogue.png)

![오프닝 한국어 자막](docs/images/opening-caption.png)

'''
    limitations = '''## 검수 기록

노부나가의 오프닝 구호와 영상의 짧은 응답 2구간은 청취 미확정입니다. 원본 특수 방별 선택 분기 7행은 완전히 재현하지 못했습니다.

- [통합 패처 실제 적용과 전체 ISO 검증](docs/verification/patcher-v0.801.json)
- [수정 XBE 네이티브 출력 검사](docs/verification/hdd-text-fix.json)
- [텍스트 재검수](docs/TEXT_REVIEW.md)
- [기본 한글판 실기 호환성 데이터 검사](docs/HARDWARE_DATA_AUDIT.md)

'''
    rebuild = '''## 패처 소스 재빌드

유지보수용 통합 이미지 조립 도구는 로컬 일본판 원본 ISO와 v0.8 ISO에서 동일한 v0.801 ISO를 만듭니다. 일반 사용자는 위 Windows 패처만 실행하면 됩니다.

```powershell
python tools/build_integrated_iso.py --original-iso "일본판 원본.iso" --base-iso "v0.8 결과.iso" --output "통합 v0.801.iso"
python tools/make_patch.py --source "일본판 원본.iso" --target "통합 v0.801.iso" --xdelta "xdelta3.exe"
python tools/package_release.py --source "일본판 원본.iso" --target "통합 v0.801.iso" --decoder "xdelta3.exe"
python tools/verify_release.py --source "일본판 원본.iso" --base-v08 "v0.8 결과.iso" --output "검증 v0.801.iso"
```

패키징은 Python 3.11 이상과 Windows .NET Framework C# 컴파일러를 사용합니다. [Xdelta 3.2.1](https://github.com/jmacd/xdelta/releases/tag/v3.2.1)의 LZMA 지원 Windows x86-64 `xdelta3.exe`가 필요합니다. 게임 자료와 완성 ISO는 저장소에 포함하지 않습니다. 외부 구성 요소의 출처와 라이선스는 [licenses](licenses/THIRD-PARTY.md)에 있습니다. 게임과 원본 그래픽의 권리는 각 권리자에게 있습니다.
'''
    (ROOT / 'README.md').write_text(head + instructions + scope + changes + screenshots + limitations + rebuild, 'utf8')
    # Release bodies use absolute main-branch links. The v0.801 tag predates this
    # corrected packaging; it is preserved rather than silently retagged.
    raw = 'https://raw.githubusercontent.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr/main/'
    body = head + instructions + changes + screenshots + limitations
    for path in ['docs/images/title.png', 'docs/images/dialogue.png', 'docs/images/opening-caption.png']:
        body = body.replace('](' + path + ')', '](' + raw + path + ')')
    for path in ['HASHES-v0.801.md', 'SHA256SUMS.txt', 'docs/verification/patcher-v0.801.json',
                 'docs/verification/hdd-text-fix.json', 'docs/TEXT_REVIEW.md', 'docs/HARDWARE_DATA_AUDIT.md']:
        body = body.replace('](' + path + ')', '](' + REPO + '/blob/main/' + path + ')')
    body += '\n2026-11-22: XBE 교체용 배포를 일본판 원본용 통합 ISO 패처로 변경했습니다. 기존 v0.801 태그는 유지하며, 갱신된 패처 소스와 검증 기록은 main 브랜치에 있습니다.\n'
    for p in (ROOT / 'RELEASE_NOTES.md', ROOT / 'docs/releases/v0.801.md'):
        p.write_text(body, 'utf8')


if __name__ == '__main__':
    main()
