"""Package the audited, self-contained full Korean ISO as a Windows delta patcher.

No game ISO, extracted game files or XBE is included in the release assets.
"""
import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr'
DECODER_HASH = '2081fb24a7b8a89d068b58e7d9353647d5fc1512a68bb6a37f71fc60ca84d943'


def hashes(path):
    hs = {n: hashlib.new(n) for n in ('md5', 'sha1', 'sha256')}
    with path.open('rb') as f:
        while block := f.read(8 * 1024 * 1024):
            for h in hs.values():
                h.update(block)
    return dict(bytes=path.stat().st_size, **{n: h.hexdigest() for n, h in hs.items()})


def main():
    ap = argparse.ArgumentParser()
    for name in ('source', 'target', 'decoder'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--csc', type=Path, default=Path('C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe'))
    args = ap.parse_args()
    c = json.loads((ROOT / 'release-config.json').read_text('utf8'))
    version = c['version']; prefix = 'XBOX-Genma-Onimusha-Kr-' + version
    proof = json.loads((ROOT / c['proof']).read_text('utf8'))
    assert proof['status'] == 'passed' and proof['hashes']['sha256'] == c['output_sha256']
    assert proof['xbe_sha256'] == c['xbe_sha256'] and not c['stock_xbe_unchanged']
    for name in ('quality', 'retail_parity'):
        p = json.loads((ROOT / c['verification_directory'] / (name + '.json')).read_text('utf8'))
        assert p['status'] == 'passed' and p['candidate_sha256'] == c['xbe_sha256']
    build, dist = ROOT / 'build', ROOT / 'dist'
    build.mkdir(exist_ok=True); dist.mkdir(exist_ok=True)
    patch = ROOT / 'patches' / (prefix + '.xdelta')
    print('Checking source ISO, target ISO, delta and decoder', flush=True)
    source, target, delta, decoder = [hashes(p) for p in (args.source, args.target, patch, args.decoder)]
    assert source['sha256'] == c['source_sha256'] and source['bytes'] == c['source_bytes']
    assert target['sha256'] == c['output_sha256'] and target['bytes'] == c['output_bytes']
    assert decoder['sha256'] == DECODER_HASH
    fields = dict(PatchHash=delta['sha256'], DecoderHash=decoder['sha256'], OutputHash=target['sha256'],
                  XbeHash=c['xbe_sha256'], Version=version, AssemblyVersion=c['assembly_version'],
                  Title=prefix, Workflow=c['workflow'])
    resources = 'namespace GenmaKorean { public static class Resources {\n'
    resources += ''.join(f'public const string {k}={json.dumps(v, ensure_ascii=False)};\n' for k, v in fields.items())
    resources += f'public const long OutputBytes={target["bytes"]}L, PatchBytes={delta["bytes"]}L, DecoderBytes={decoder["bytes"]}L;\n'
    resources += f'public const int XbeBytes={c["xbe_bytes"]}; public const long XbeOffset={c["xbe_offset"]}L; public const bool StockXbe=false;\n}} }}\n'
    (build / 'Resources.cs').write_text(resources, 'utf8')
    exe = dist / (prefix + '-Patcher.exe')
    assert not exe.exists(), 'Refusing to replace a previously packaged EXE'
    subprocess.run([str(args.csc), '/nologo', '/target:winexe', '/platform:x64', '/optimize+', '/utf8output',
                    f'/out:{exe}', '/reference:System.Windows.Forms.dll', '/reference:System.Drawing.dll',
                    '/reference:System.Web.Extensions.dll', f'/resource:{patch},patch',
                    f'/resource:{args.decoder},decoder', str(ROOT / 'src/Patcher.cs'), str(build / 'Resources.cs')], check=True)
    info = json.loads(subprocess.check_output([str(exe), '--info'], text=True, encoding='utf8'))
    assert info['version'] == version and info['source_sha256'] == source['sha256']
    assert info['output_sha256'] == target['sha256'] and info['patch_sha256'] == delta['sha256']
    assert info['integrated_xbe_sha256'] == c['xbe_sha256'] and info['output_format'] == 'single ISO'
    assert not info['stock_xbe_unchanged']
    manifest = dict(version=version, release_type='self-contained full Korean single ISO patcher', repository=REPO,
                    source=dict(name='Genma Onimusha (Japan) (En,Ja).iso', **source),
                    output=dict(name=prefix + '.iso', **target), patch=dict(name=patch.name, **delta),
                    patcher=dict(name=exe.name, **hashes(exe)), decoder=dict(version='3.2.1', **decoder),
                    integrated_default_xbe=dict(bytes=c['xbe_bytes'], offset=c['xbe_offset'], sha256=c['xbe_sha256'],
                                                sections=24, unchanged_from_japanese_original=False),
                    stock_xbe_unchanged=False, original_certificate_preserved=True,
                    external_xbe_replacement_required=False, external_runtime_loader_required=False,
                    external_runtime_plugin_required=False, external_runtime_config_required=False,
                    fixed_ui_rows_translated=327, timed_movie_cues=86, native_render_cases_equal=5219,
                    saved_preload_bytes=143360, text_language_setting='Japanese',
                    pc_cxbx_retail_title_verified=True, physical_xbox_verified=False,
                    xbox360_execution_verified=False, full_gameplay_verified=False)
    instructions = f'''환마 귀무자 (Genma Onimusha) 한국어 패치 {version}
한글화: 기타 깎는 노인

일본판 원본 ISO에서 전체 한글화를 포함한 ISO 한 파일을 만듭니다.
수정 default.xbe와 한글 데이터가 ISO 안에 들어 있습니다.
한글화를 위한 별도 로더·RAM 패처·플러그인·설정 파일은 필요 없습니다.
기존 구엑박 게임 실행 환경과 일반적인 설치 절차는 필요합니다.

1. {exe.name}를 실행합니다.
2. Genma Onimusha (Japan) (En,Ja) 원본 ISO를 선택합니다.
3. 새 ISO 저장 위치를 고르고 [한글 패치 시작]을 누릅니다.
4. 결과 ISO SHA-256 및 내부 XBE 검증과 완료 메시지를 기다립니다.
5. 게임의 문자 언어는 日本語(일본어)로 두세요. 음성 설정은 별개입니다.

Windows 10/11 64비트용입니다. Python 설치는 필요 없습니다.
출력 위치에 6GB 이상, 임시 폴더에 200MB 이상의 빈 공간이 필요합니다.
결과 ISO는 4GB를 넘으므로 NTFS 또는 exFAT에 저장하세요.
원본과 기존 출력 파일은 덮어쓰지 않습니다. 이미 패치한 ISO는 입력으로 지원하지 않습니다.
이전 버전 선행 적용이나 default.xbe 수동 교체는 필요 없습니다.

v0.802에서 일본어로 남겼던 메뉴·아이템명·설명·선택지를 한글화합니다.
대사·문서·이미지 UI와 오프닝을 포함한 영상 자막·크레딧을 포함합니다.
일본판 인증서·지역·매체 값, 기존 23개 섹션 배치를 유지합니다.
한글 코드와 데이터용 KRDATA 섹션 1개를 추가한 수정 XBE입니다.

지원 원본 크기: {source['bytes']:,} bytes
지원 원본 SHA-256: {source['sha256']}
결과 ISO 크기: {target['bytes']:,} bytes
결과 ISO SHA-256: {target['sha256']}
ISO 내부 default.xbe SHA-256: {c['xbe_sha256']}

PC Cxbx Retail 모드의 타이틀 진입과 데이터 검사를 통과했습니다.
Xbox 360/XeFu 및 실기 Xbox 실행과 전체 플레이는 미검증입니다.
기존 실행 불가 제보가 해결되었다고 보장하는 버전은 아닙니다.
원본 게임 ISO는 포함하지 않습니다. 결과는 XDVDFS 게임 이미지입니다.
5GB ISO는 FATX 단일 파일 제한을 넘습니다. 사용하는 실행 환경에 맞게
일반적인 설치용 추출·변환 절차를 진행하세요.

{REPO}/releases/tag/{version}
'''
    usage, hashfile = dist / (prefix + '-사용법.txt'), dist / (prefix + '-HASHES.txt')
    usage.write_text(instructions, 'utf-8-sig')
    hashfile.write_text('\n\n'.join(f"{label}\n크기: {h['bytes']:,} bytes\nSHA-256: {h['sha256']}"
                        for label, h in [('일본판 원본 ISO', source), (version + ' 결과 ISO', target),
                                         (patch.name, delta), (exe.name, manifest['patcher'])]) + '\n', 'utf-8-sig')
    archive = dist / (prefix + '-Windows-Patcher.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p, name in [(exe, exe.name), (usage, '사용법.txt'), (hashfile, 'HASHES.txt')]:
            z.write(p, name)
        for p in sorted((ROOT / 'licenses').iterdir()):
            if p.is_file(): z.write(p, 'licenses/' + p.name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert hashlib.sha256(z.read(exe.name)).hexdigest() == manifest['patcher']['sha256']
    manifest['assets'] = [dict(name=p.name, **hashes(p)) for p in (exe, archive, patch, hashfile)]
    for p in (ROOT / 'release-manifest.json', ROOT / f'release-manifest-{version}.json', dist / f'release-manifest-{version}.json'):
        p.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', 'utf8')
    sums = ''.join(f"{h['sha256']}  {h['name']}\n" for h in manifest['assets'])
    for p in (ROOT / 'SHA256SUMS.txt', dist / (prefix + '-SHA256SUMS.txt')):
        p.write_text(sums, 'utf8')
    table = '| 대상 | 크기 (bytes) | MD5 | SHA-1 | SHA-256 |\n| --- | ---: | --- | --- | --- |\n'
    for label, h in [('일본판 원본 ISO', source), (version + ' 단일 ISO', target),
                     (exe.name, manifest['patcher']), (patch.name, delta)]:
        table += f"| {label} | {h['bytes']:,} | `{h['md5']}` | `{h['sha1']}` | `{h['sha256']}` |\n"
    table += f'\nISO 내부 수정 `default.xbe` SHA-256: `{c["xbe_sha256"]}`\n\n## 배포 파일 SHA-256\n\n```text\n{sums}```\n'
    for p in (ROOT / 'HASHES.md', ROOT / f'HASHES-{version}.md'):
        p.write_text('# ' + version + ' 단일 ISO 패치 파일 해시\n\n' + table, 'utf8')
    print(json.dumps(dict(version=version, patcher=manifest['patcher'], assets=manifest['assets']), ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
