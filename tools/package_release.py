"""Build the configured Japanese-original-to-single-ISO Windows patcher."""
import argparse
import json
import subprocess
import zipfile
from pathlib import Path
from build_integrated_iso import SOURCE as SOURCE_HASH, digests as hashes

ROOT = Path(__file__).resolve().parents[1]
CONFIG=json.loads((ROOT/'release-config.json').read_text('utf8'))
VERSION = CONFIG['version']
FIXED=CONFIG['xbe_sha256']
PREFIX = 'XBOX-Genma-Onimusha-Kr-' + VERSION
REPO = 'https://github.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr'
DECODER_HASH = '2081fb24a7b8a89d068b58e7d9353647d5fc1512a68bb6a37f71fc60ca84d943'


def main():
    ap = argparse.ArgumentParser()
    for name in ('source', 'target', 'decoder'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--csc', type=Path, default=Path('C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe'))
    args = ap.parse_args()
    build, dist = ROOT / 'build', ROOT / 'dist'
    build.mkdir(exist_ok=True)
    dist.mkdir(exist_ok=True)
    proof = json.loads((ROOT / CONFIG['proof']).read_text('utf8'))
    assert proof['iso']['status'] == 'passed' and proof['iso']['default_xbe_sha256'] == FIXED
    print('Checking source, integrated target, delta and decoder', flush=True)
    source, target = hashes(args.source), hashes(args.target)
    patch = ROOT / 'patches' / (PREFIX + '.xdelta')
    delta, decoder = hashes(patch), hashes(args.decoder)
    assert source['sha256'] == SOURCE_HASH and source['bytes'] == 4905566208
    assert target['sha256'] == CONFIG['output_sha256'] and target['bytes'] == CONFIG['output_bytes']
    assert decoder['sha256'] == DECODER_HASH
    fields = dict(PatchHash=delta['sha256'], DecoderHash=decoder['sha256'], OutputHash=target['sha256'], XbeHash=FIXED,
                  Version=VERSION,AssemblyVersion=CONFIG['assembly_version'],Title=PREFIX,Workflow=CONFIG['workflow'])
    resources = 'namespace GenmaKorean { public static class Resources {\n'
    resources += ''.join(f'public const string {k}="{v}";\n' for k, v in fields.items())
    resources += f'public const long OutputBytes={target["bytes"]}L;\n' + '} }\n'
    resources = resources.replace('} }', f'public const long PatchBytes={delta["bytes"]}L, DecoderBytes={decoder["bytes"]}L;\n' + '} }')
    resources = resources.replace('} }', f'public const int XbeBytes={CONFIG["xbe_bytes"]}; public const long XbeOffset={CONFIG["xbe_offset"]}L; public const bool StockXbe=true;\n' + '} }')
    (build / 'Resources.cs').write_text(resources, 'utf8')
    exe = dist / (PREFIX + '-Patcher.exe')
    subprocess.run([str(args.csc), '/nologo', '/target:winexe', '/platform:x64', '/optimize+', '/utf8output',
                    f'/out:{exe}', '/reference:System.Windows.Forms.dll', '/reference:System.Drawing.dll',
                    '/reference:System.Web.Extensions.dll', f'/resource:{patch},patch',
                    f'/resource:{args.decoder},decoder', str(ROOT / 'src/Patcher.cs'), str(build / 'Resources.cs')], check=True)
    info = json.loads(subprocess.check_output([str(exe), '--info'], text=True, encoding='utf8'))
    assert info['version'] == VERSION and info['source_sha256'] == SOURCE_HASH
    assert info['output_sha256'] == target['sha256'] and info['patch_sha256'] == delta['sha256']
    assert info['integrated_xbe_sha256'] == FIXED and info['output_format'] == 'single ISO' and info['stock_xbe_unchanged']
    manifest = dict(version=VERSION, release_type='stock-XBE data-only single ISO compatibility patcher', repository=REPO,
                    internal_content_revision='20261122 stock-XBE compatibility data',
                    source=dict(name='Genma Onimusha (Japan) (En,Ja).iso', **source),
                    output=dict(name=PREFIX + '.iso', **target), patch=dict(name=patch.name, **delta),
                    patcher=dict(name=exe.name, **hashes(exe)), decoder=dict(version='3.2.1', **decoder),
                    integrated_default_xbe=dict(bytes=CONFIG['xbe_bytes'],offset=CONFIG['xbe_offset'],sha256=FIXED,sections=23,unchanged_from_japanese_original=True),
                    requires_existing_korean_v08_game_folder=False, external_xbe_replacement_required=False,
                    native_korean_pages=proof['cpu']['pages_executed'],native_loader_cases=proof['cpu']['loader_cases'],
                    fixed_ui_rows_retained_in_japanese=327,additional_injected_opening_movie_credit_hooks=False,
                    native_caption_movies=2,text_language_setting='Japanese',stock_xbe_unchanged=True,
                    physical_xbox_verified=False,full_gameplay_verified=False)
    instructions = f'''환마 귀무자 (Genma Onimusha) 한국어 패치 {VERSION}
한글화: 기타 깎는 노인

일본판 원본 ISO에서 {VERSION} 한글 ISO 한 파일을 만듭니다.
default.xbe는 일본판 원본과 바이트 단위로 동일하게 유지합니다.
v0.8 선행 적용이나 default.xbe 수동 교체는 필요 없습니다.

1. {exe.name}를 실행합니다.
2. Genma Onimusha (Japan) (En,Ja) 원본 ISO를 선택합니다.
3. 새 ISO 저장 위치를 고르고 [한글 패치 시작]을 누릅니다.
4. 결과 ISO SHA-256 검증과 완료 메시지를 기다립니다.

Windows 10/11 64비트용입니다. Python 설치는 필요 없습니다.
출력 위치에 6GB 이상, 임시 폴더에 200MB 이상의 빈 공간이 필요합니다.
결과 ISO는 4GB를 넘으므로 NTFS 또는 exFAT에 저장하세요.
원본과 기존 출력 파일은 덮어쓰지 않습니다. 이미 패치한 ISO는 입력으로 지원하지 않습니다.
기존 한글판 사용자도 일본판 원본 ISO에서 새로 생성하면 됩니다.

게임의 문자 언어는 日本語(일본어)로 두세요. 음성 설정은 별개입니다.
대사·문서·이미지 메뉴와 원래 자막이 있던 영상 두 편을 한글화합니다.
XBE 내부 아이템명·메뉴·설명·선택지 327항목은 일본어 원문을 유지합니다.
추가 영상·오프닝 음성 자막과 한글 크레딧 코드는 포함하지 않습니다.

지원 원본 크기: {source['bytes']:,} bytes
지원 원본 SHA-256: {source['sha256']}
결과 ISO 크기: {target['bytes']:,} bytes
결과 ISO SHA-256: {target['sha256']}
ISO 내부 default.xbe SHA-256: {FIXED}

별도 로더나 메모리 코드 패치 없이 원본 XBE가 번역 데이터를 읽습니다.
실기 Xbox 부팅과 전체 플레이는 미검증입니다.
원본 게임 ISO는 포함하지 않습니다. 결과는 XDVDFS 게임 이미지입니다.
실기 설치용 파일 추출이나 이미지 변환은 사용하는 로더의 형식에 맞게 진행하세요.

{REPO}/releases/tag/{VERSION}
'''
    usage, hashfile = dist / (PREFIX + '-사용법.txt'), dist / (PREFIX + '-HASHES.txt')
    usage.write_text(instructions, 'utf-8-sig')
    hashfile.write_text('\n\n'.join(f"{label}\n크기: {h['bytes']:,} bytes\nSHA-256: {h['sha256']}"
                        for label, h in [('일본판 원본 ISO', source), (VERSION+' 결과 ISO', target),
                                         (patch.name, delta), (exe.name, manifest['patcher'])]) + '\n', 'utf-8-sig')
    archive = dist / (PREFIX + '-Windows-Patcher.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p, name in [(exe, exe.name), (usage, '사용법.txt'), (hashfile, 'HASHES.txt')]:
            z.write(p, name)
        for p in sorted((ROOT / 'licenses').iterdir()):
            if p.is_file():
                z.write(p, 'licenses/' + p.name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        import hashlib
        assert hashlib.sha256(z.read(exe.name)).hexdigest() == manifest['patcher']['sha256']
    manifest['assets'] = [dict(name=p.name, **hashes(p)) for p in (exe, archive, patch, hashfile)]
    for p in (ROOT / 'release-manifest.json', ROOT / f'release-manifest-{VERSION}.json', dist / f'release-manifest-{VERSION}.json'):
        p.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', 'utf8')
    sums = ''.join(f"{h['sha256']}  {h['name']}\n" for h in manifest['assets'])
    for p in (ROOT / 'SHA256SUMS.txt', dist / (PREFIX + '-SHA256SUMS.txt')):
        p.write_text(sums, 'utf8')
    table = '| 대상 | 크기 (bytes) | MD5 | SHA-1 | SHA-256 |\n| --- | ---: | --- | --- | --- |\n'
    for label, h in [('일본판 원본 ISO', source), (VERSION+' 원본 XBE 호환판 ISO', target),
                     (exe.name, manifest['patcher']), (patch.name, delta)]:
        table += f"| {label} | {h['bytes']:,} | `{h['md5']}` | `{h['sha1']}` | `{h['sha256']}` |\n"
    table += f'\nISO 내부 `default.xbe` SHA-256: `{FIXED}`\n\n## 배포 파일 SHA-256\n\n```text\n{sums}```\n'
    for p in (ROOT / 'HASHES.md', ROOT / f'HASHES-{VERSION}.md'):
        p.write_text('# '+VERSION+' 원본 XBE 호환판 파일 해시\n\n' + table, 'utf8')
    print(json.dumps(manifest, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
