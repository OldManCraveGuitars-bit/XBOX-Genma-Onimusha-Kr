"""Package the verified original-layout replacement as the v0.801 update."""
import argparse,hashlib,json,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VERSION='v0.801'
PREFIX='XBOX-Genma-Onimusha-Kr-v0.801'
FIXED='81a65ca47a0e5d72944895a7b0aa0eee609689c1aa0896041ce3c1a95f45664c'
REPO='OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr'

def digests(data):return {name:hashlib.new(name,data).hexdigest() for name in ('md5','sha1','sha256')}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fixed-xbe',type=Path,required=True);ap.add_argument('--verification',type=Path,required=True);args=ap.parse_args()
    data=args.fixed_xbe.read_bytes();checks=json.loads(args.verification.read_text('utf8'))
    assert len(data)==3510272 and hashlib.sha256(data).hexdigest()==FIXED
    assert checks['status']=='passed' and checks['fixed_xbe_sha256']==FIXED
    assert checks['korean_native_output_cases_exactly_equal']==5219 and len(checks['checks'])==12
    assert all(c['status']=='passed' for c in checks['checks'])
    dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    instruction=f'''환마 귀무자 한국어 패치 v0.801 · XBE 교체 업데이트
한글화: 기타 깎는 노인

적용 대상: v0.8 한글화 데이터를 폴더로 풀어 놓은 게임

1. 기존 v0.8 한글 게임 폴더의 default.xbe를 다른 곳에 백업합니다.
2. 이 압축파일의 default.xbe를 게임 폴더 최상단에 복사해 교체합니다.
3. 나머지 v0.8 한글화 데이터는 그대로 사용합니다.

이미 일본판 원본 default.xbe로 교체한 뒤 한글이 깨진 상태에도 같은 방법으로 적용합니다.
처음 설치하는 경우 먼저 v0.8 기본 한글 패치를 적용해야 합니다.
ISO 한 파일 안의 XBE를 자동 교체하는 프로그램은 아닙니다. 폴더로 풀어 놓은 게임에 적용하세요.
순정 일본판 데이터에 이 파일 하나만 넣어 전체 한글화를 하는 용도는 아닙니다.

이 파일은 원본의 23개 섹션 구조를 사용하는 수정 XBE입니다.
한글 처리 코드·문자열·자막 데이터는 유지하며, HDD 매체 허용과 파일 끝 정렬을 보정했습니다.
원본 일본판 XBE를 무수정으로 사용하는 방식은 아닙니다.

검사: 본문 3,768페이지를 포함한 5,219개 네이티브 출력 조건이 정상 한글판과 일치했습니다.
글리프 초기화/해제, 메뉴·아이템·저장·선택지·문서·영상 자막·크레딧 12종 검사가 통과했습니다.
이 결과는 CPU 함수·데이터 검사입니다. 실기 Xbox 부팅과 전체 플레이는 미검증입니다.
테스트 업데이트이며 실기 실행 불가의 원인이나 해결을 확정한 배포물로 표시하지 않습니다.

default.xbe SHA-256: {FIXED}
릴리스: https://github.com/{REPO}/releases/tag/{VERSION}
기본 v0.8: https://github.com/{REPO}/releases/tag/v0.8
'''
    verification=dict(version=VERSION,base_version='v0.8',test_release=True,korean_output_verified=True,physical_boot_verified=False,checks=checks)
    archive=dist/(PREFIX+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.writestr('default.xbe',data)
        z.writestr('적용방법.txt',instruction.encode('utf-8-sig'))
        z.writestr('SHA256SUMS.txt',f'{FIXED}  default.xbe\n')
        z.writestr('verification.json',json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and z.read('default.xbe')==data
        assert z.read('적용방법.txt').decode('utf-8-sig')==instruction
    ah=digests(archive.read_bytes());xh=digests(data)
    manifest=dict(version=VERSION,base_version='v0.8',release_type='test XBE replacement update',repository=f'https://github.com/{REPO}',
                  requires_existing_korean_v08_game_folder=True,original_iso_included=False,
                  default_xbe=dict(bytes=len(data),**xh),archive=dict(name=archive.name,bytes=archive.stat().st_size,**ah),
                  original_layout_sections=23,native_output_conditions=5219,body_pages=3768,
                  code_or_translation_changed_since_verified_fix=False,korean_output_verified=True,physical_boot_verified=False)
    for p in (ROOT/'release-manifest-v0.801.json',dist/'release-manifest-v0.801.json'):
        p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    sums=f"{ah['sha256']}  {archive.name}\n{FIXED}  default.xbe\n"
    (dist/(PREFIX+'-SHA256SUMS.txt')).write_text(sums,'ascii')
    hashes='# v0.801 파일 해시\n\n| 파일 | 크기 (bytes) | MD5 | SHA-1 | SHA-256 |\n| --- | ---: | --- | --- | --- |\n'
    for name,size,h in [('default.xbe',len(data),xh),(archive.name,archive.stat().st_size,ah)]:
        hashes+=f"| {name} | {size:,} | `{h['md5']}` | `{h['sha1']}` | `{h['sha256']}` |\n"
    (ROOT/'HASHES-v0.801.md').write_text(hashes,'utf8')
    raw=f'https://raw.githubusercontent.com/{REPO}/{VERSION}'
    notes=f'''![환마 귀무자 한국어 타이틀 화면]({raw}/docs/images/title.png)

# XBOX-Genma-Onimusha-Kr v0.801

**기존 v0.8 한글 데이터에 적용하는 XBE 교체 테스트 업데이트입니다.**

한글화: **기타 깎는 노인**

## 적용 방법

1. `{archive.name}`을 받아 압축을 풉니다.
2. **폴더로 풀어 놓은 v0.8 한글 게임**의 기존 `default.xbe`를 백업합니다.
3. ZIP의 `default.xbe`를 게임 폴더 최상단에 복사해 교체합니다.
4. 나머지 한글화 데이터는 그대로 사용합니다. 이미 일본판 원본 XBE로 바꿔 한글이 깨진 상태에도 같은 방법으로 적용합니다.

처음 설치한다면 먼저 [v0.8 기본 한글 패치](https://github.com/{REPO}/releases/tag/v0.8)를 적용해야 합니다. v0.801은 전체 ISO 패처가 아니며, 순정 일본판 게임에 이 파일 하나만 넣어 전체 한글화를 하는 용도가 아닙니다.

## 변경 내용

이 파일도 **수정 XBE**입니다. 원본의 23개 섹션 구조와 기존 헤더·이름·참조 포인터 배치를 유지하면서, 한글 처리 코드·문자열·자막 데이터를 포함합니다. 기본 v0.8의 24개 섹션 구성에서 배치를 바꿨습니다. HDD 매체 허용과 파일 끝 정렬을 보정했습니다.

기존 한글 코드·문자열·그림과 원본 타이틀 아이콘은 유지합니다. 일본판 원본 XBE를 무수정으로 사용하는 방식은 아닙니다.

## 검수 범위

본문 **3,768페이지를 포함한 5,219개 네이티브 출력 조건**이 정상 한글판과 일치했습니다. 글리프 초기화·해제, 메뉴·아이템·저장·선택지·문서·영상 자막·크레딧 12종 검사를 통과했습니다. 이번 패키지의 XBE 해시는 검사한 파일과 동일합니다.

**실기 Xbox 부팅과 전체 플레이는 미검증입니다.** CPU 함수·데이터 검사 결과를 바탕으로 올리는 테스트 릴리스이며, 제보된 실기 실행 불가가 해결됐다고 확정하는 배포물은 아닙니다.

## SHA-256

```text
{sums.rstrip()}
```

[MD5·SHA-1·SHA-256 전체 목록](https://github.com/{REPO}/blob/{VERSION}/HASHES-v0.801.md) · [파일 검증 기록](https://github.com/{REPO}/blob/{VERSION}/release-manifest-v0.801.json)

## 스크린샷

기존 개발 중 확보한 에뮬레이터 캡처입니다. v0.801 실기 실행 캡처는 아닙니다.

![한국어 대사]({raw}/docs/images/dialogue.png)

![오프닝 한국어 자막]({raw}/docs/images/opening-caption.png)
'''
    folder=ROOT/'docs/releases';folder.mkdir(exist_ok=True)
    old=ROOT/'RELEASE_NOTES.md';saved=folder/'v0.8-notes.md'
    if not saved.exists():saved.write_text(old.read_text('utf8'),'utf8')
    for path in (old,folder/'v0.801.md'):path.write_text(notes,'utf8')
    current=(ROOT/'README.md').read_text('utf8')
    current=current.replace('# XBOX-Genma-Onimusha-Kr · v0.8\n','# XBOX-Genma-Onimusha-Kr · v0.801\n',1)
    start=current.index('## 원본 XBE 교체 후 한글 깨짐 수정')
    end=current.index('## 한글화 범위',start)
    intro=f'''## v0.801 테스트 업데이트

**기존 v0.8 한글 게임 폴더의 `default.xbe`를 교체하는 업데이트입니다.**

[v0.801 다운로드](https://github.com/{REPO}/releases/tag/{VERSION}) · [적용 방법](docs/releases/v0.801.md) · [파일 해시](HASHES-v0.801.md)

이것도 한글 코드가 들어간 수정 XBE이며, 원본의 23개 섹션 구조를 사용합니다. 5,219개 네이티브 출력 검사를 통과했습니다. **실기 부팅과 전체 플레이는 미검증입니다.**

처음 설치할 때는 [v0.8 기본 한글 패치](https://github.com/{REPO}/releases/tag/v0.8)를 먼저 적용하세요. v0.801에는 교체용 XBE와 적용 안내만 들어 있습니다.

'''
    current=current[:start]+intro+current[end:]
    current=current.replace('## 다운로드와 적용\n','## 기본 v0.8 다운로드와 적용\n',1)
    current=current.replace('### v0.8 결과 ISO\n','### 기본 v0.8 결과 ISO\n',1)
    assert current.startswith('![') and '## v0.801 테스트 업데이트' in current
    (ROOT/'README.md').write_text(current,'utf8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
