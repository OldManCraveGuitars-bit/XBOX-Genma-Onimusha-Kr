"""Assemble the public release notes after the executable roundtrip passes."""
import argparse,hashlib,json,shutil
from pathlib import Path
from package_release import ROOT,PREFIX

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True);args=ap.parse_args()
    manifest=json.loads((ROOT/'release-manifest.json').read_text('utf8'))
    patcher=json.loads((ROOT/'docs/verification/patcher-v0.8.json').read_text('utf8'))
    assert patcher['status']=='passed' and patcher['patcher_sha256']==manifest['patcher']['sha256']
    review=json.loads((args.project/'analysis/review_r16/review_summary.json').read_text('utf8'))
    comparison=json.loads((args.project/'analysis/Genma-Onimusha-KR-20261121-r16.comparison.json').read_text('utf8'))
    assert comparison['output_sha256']==manifest['output']['sha256'] and comparison['unexpected_changed_bytes']==0
    manifest['windows_exe_roundtrip_verified']=True
    manifest['guards_passed']=len(patcher['cases'])-1
    (ROOT/'release-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    evidence=dict(text_review=review,iso_comparison={k:v for k,v in comparison.items() if not k.endswith('_path')},
                  screenshots=dict(origin='Previously recorded emulator execution captures; not a fresh v0.8 playthrough',images=['title.png','dialogue.png','opening-caption.png']))
    (ROOT/'docs/verification/content-v0.8.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n','utf8')
    for source,destination in [('output/TEXT_REVIEW_r16.md','docs/TEXT_REVIEW.md'),('output/HARDWARE_DATA_AUDIT_r15.md','docs/HARDWARE_DATA_AUDIT.md')]:
        text=(args.project/source).read_text('utf8').replace('analysis/review_r16/corrected_text.native-projection.png','verification/corrected-text.png')
        heading,body=text.split('\n',1)
        note='아래는 내부 개발본의 검수 기록입니다. 현재 v0.8 공개 배포물과 해시는 [HASHES.md](../HASHES.md)를 기준으로 확인하세요. 기록의 `GenmaKoreanTool-r15.exe`는 개발용 편집기이며, 공개 배포하는 Windows 패처와 별개입니다.'
        text=heading+'\n\n'+note+'\n'+body
        text=text.replace(' 실기 검증을 요청하거나 요구하지 않았습니다.','')
        (ROOT/destination).write_text(text,'utf8')
    shutil.copyfile(args.project/'analysis/review_r16/corrected_text.native-projection.png',ROOT/'docs/verification/corrected-text.png')
    repo='OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr'
    raw=f'https://raw.githubusercontent.com/{repo}/v0.8'
    sums=(ROOT/'SHA256SUMS.txt').read_text('utf8')
    notes=f'''![환마 귀무자 한국어 타이틀 화면]({raw}/docs/images/title.png)

# 환마 귀무자 한국어 패치 v0.8

Xbox용 **환마 귀무자 (Genma Onimusha)** 일본판 한국어 패치입니다.

**한글화: 기타 깎는 노인**

## 적용 범위

대사·조사문·아이템 이름과 설명, 타이틀·설정·조작·저장·지도·강화 메뉴, 문서·지침서·암호책 설명, 이미지 메뉴·랭크, 영상 자막과 오프닝 편지 낭독 자막을 한글화했습니다.

궁서·붓글씨 분위기를 유지하며 글꼴, 숫자, 테두리, 문서 여백과 선택지 간격을 보수했습니다. 원래 암호 퍼즐의 문자와 수집 조건은 유지합니다. 오프닝 일본어 편지 원화에는 음성에 맞춘 가로 한국어 자막을 표시합니다.

v0.8은 내부 검수본 r16까지의 수정 사항을 포함합니다. 최신 텍스트 검수에서 조사문 의미·관찰 표현·인물 말투 5행을 보완했고, 확대 글꼴 처리 중 원본 범위를 벗어나는 읽기를 막는 수정도 반영했습니다.

## 다운로드 · 사용법

1. **`{PREFIX}-Windows-Patcher.zip`**을 받아 압축을 풉니다. 단독 `-Patcher.exe`도 같은 기능입니다.
2. Windows 패처에서 `Genma Onimusha (Japan) (En,Ja)` 원본 ISO를 선택합니다.
3. 새 ISO 저장 위치를 지정하고 **한글 패치 시작**을 누릅니다.
4. 결과 SHA-256 검사와 완료 메시지를 확인합니다.

Windows 10/11 64비트용이며 Python 설치가 필요 없습니다. 출력 드라이브에 **5.5GB 이상**의 빈 공간을 확보하세요. 결과 ISO는 4GB를 넘으므로 NTFS 또는 exFAT에 저장해야 합니다. 원본과 기존 출력은 덮어쓰지 않습니다. `.xdelta`는 별도 적용 도구를 쓰는 사용자를 위한 파일입니다.

원본 게임 ISO는 포함하지 않습니다. 지원하는 일본판 원본과 해시가 같아야 적용됩니다.

## 원본·결과 ISO SHA-256

| 구분 | 크기 (bytes) | SHA-256 |
| --- | ---: | --- |
| Japan (En,Ja) 원본 | {manifest['source']['bytes']:,} | `{manifest['source']['sha256']}` |
| v0.8 결과 | {manifest['output']['bytes']:,} | `{manifest['output']['sha256']}` |

MD5·SHA-1·SHA-256 전체 목록은 [HASHES.md](https://github.com/{repo}/blob/v0.8/HASHES.md)에 있습니다.

### 배포 파일 SHA-256

```text
{sums.rstrip()}
```

## 스크린샷

개발 중 확보한 에뮬레이터 실행 캡처입니다. 모든 화면을 v0.8에서 다시 촬영한 자료는 아닙니다.

![한국어 대사]({raw}/docs/images/dialogue.png)

![오프닝 가로 자막]({raw}/docs/images/opening-caption.png)

## 검수 범위

현재 한글 본문 3,272행과 메뉴·문서·자막·이미지 문구를 다시 읽었습니다. 원본 코드의 글자 배치로 본문 3,768페이지와 메뉴·선택지 겹침·잘림을 검사했습니다. 배포 EXE로 원본 ISO 전체를 패치한 결과도 위 SHA-256과 일치하며, 잘못된 입력과 기존 파일 덮어쓰기 차단을 확인했습니다.

청취 미확정 음성 2구간과 미재현 특수 방별 선택 분기 7행이 남아 있습니다. 실기 Xbox 및 처음부터 엔딩까지 전체 플레이는 미검증입니다.

[텍스트 검수 내역](https://github.com/{repo}/blob/v0.8/docs/TEXT_REVIEW.md) · [데이터 호환성 검사](https://github.com/{repo}/blob/v0.8/docs/HARDWARE_DATA_AUDIT.md) · [배포 패처 검증](https://github.com/{repo}/blob/v0.8/docs/verification/patcher-v0.8.json)
'''
    (ROOT/'RELEASE_NOTES.md').write_text(notes,'utf8')
    for asset in manifest['assets']:
        path=ROOT/('patches' if asset['name'].endswith('.xdelta') else 'dist')/asset['name']
        with path.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==asset['sha256']
    print('Public docs, release notes, source/target hashes and download hashes verified.')

if __name__=='__main__':main()
