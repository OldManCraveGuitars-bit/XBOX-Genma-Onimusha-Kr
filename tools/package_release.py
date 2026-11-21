"""Build a self-contained Windows patcher for the verified v0.8 ISO delta."""
import argparse, hashlib, json, shutil, subprocess, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREFIX='XBOX-Genma-Onimusha-Kr-v0.8'
SOURCE_HASH='7f5af784f9b229c5d0061918e018a9052e328a5341efc7d9e1b5d36de5f58206'
OUTPUT_HASH='dbd207078fc41095afe805743277676214fc6e71d2cce2db30f0b161dc0f8dc2'

def hashes(path):
    digests={name:hashlib.new(name) for name in ('md5','sha1','sha256')}
    with path.open('rb') as f:
        while chunk:=f.read(8*1024*1024):
            for digest in digests.values(): digest.update(chunk)
    return dict(bytes=path.stat().st_size,**{name:h.hexdigest() for name,h in digests.items()})

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True); ap.add_argument('--target',type=Path,required=True)
    ap.add_argument('--decoder',type=Path,required=True)
    ap.add_argument('--csc',type=Path,default=Path('C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe'))
    args=ap.parse_args(); build=ROOT/'build'; dist=ROOT/'dist'; build.mkdir(exist_ok=True); dist.mkdir(exist_ok=True)
    patch=ROOT/'patches'/f'{PREFIX}.xdelta'; assert patch.is_file()
    print('Checking source, target and delta hashes',flush=True)
    source=hashes(args.source); target=hashes(args.target); delta=hashes(patch); decoder=hashes(args.decoder)
    assert source['sha256']==SOURCE_HASH and source['bytes']==4905566208
    assert target['sha256']==OUTPUT_HASH and target['bytes']==5385351168
    (build/'Resources.cs').write_text('namespace GenmaKorean { public static class Resources { public const string PatchHash="'+delta['sha256']+'", DecoderHash="'+decoder['sha256']+'"; } }\n','utf8')
    exe=dist/f'{PREFIX}-Patcher.exe'
    command=[str(args.csc),'/nologo','/target:winexe','/platform:x64','/optimize+','/utf8output',f'/out:{exe}',
             '/reference:System.Windows.Forms.dll','/reference:System.Drawing.dll','/reference:System.Web.Extensions.dll',
             f'/resource:{patch},patch',f'/resource:{args.decoder},decoder',str(ROOT/'src/Patcher.cs'),str(build/'Resources.cs')]
    subprocess.run(command,check=True,cwd=ROOT)
    info=json.loads(subprocess.check_output([str(exe),'--info'],text=True,encoding='utf8'))
    assert info['source_sha256']==SOURCE_HASH and info['output_sha256']==OUTPUT_HASH and info['patch_sha256']==delta['sha256']
    manifest=dict(version='v0.8',internal_content_revision='20261121-r16',repository='https://github.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr',
                  source=dict(name='Genma Onimusha (Japan) (En,Ja).iso',**source),
                  output=dict(name=f'{PREFIX}.iso',**target),patch=dict(name=patch.name,**delta),
                  patcher=dict(name=exe.name,**hashes(exe)),decoder=dict(version='3.2.1',**decoder),
                  physical_xbox_verified=False,full_gameplay_verified=False)
    (ROOT/'release-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    instructions=f'''환마 귀무자 (Genma Onimusha) 한국어 패치 v0.8
한글화 기타 깎는 노인

1. {exe.name}를 실행합니다.
2. Genma Onimusha (Japan) (En,Ja) 원본 ISO를 선택합니다.
3. 새 결과 ISO 저장 위치를 고르고 [한글 패치 시작]을 누릅니다.
4. 결과 ISO SHA-256 확인과 완료 메시지를 기다립니다.

Windows 10/11 64비트용입니다. Python 설치는 필요 없습니다.
출력 위치에 5.5GB 이상, 임시 폴더에 패치 파일 크기 이상의 빈 공간이 필요합니다.
결과 ISO는 4GB를 넘으므로 NTFS 또는 exFAT 드라이브에 저장하세요.
원본과 기존 출력 파일은 덮어쓰지 않습니다. 이미 패치된 ISO는 입력으로 지원하지 않습니다.
원본과 결과의 SHA-256을 자동 확인합니다. 중단되거나 검증에 실패한 출력은 정리합니다.
완료된 ISO는 원래 추출 형식과 같은 XDVDFS 게임 이미지입니다. 실기 설치 형식은 사용 환경에 맞게 변환하세요.

대상 원본: {source['bytes']:,} bytes
SHA-256: {SOURCE_HASH}
결과 ISO: {target['bytes']:,} bytes
SHA-256: {OUTPUT_HASH}

README, HASHES.md와 릴리스 설명에 번역 범위와 검수 한계가 있습니다.
타이틀·대사·메뉴·문서·설명·영상 자막 등을 한글화했습니다.
실기 Xbox 실행과 처음부터 끝까지의 전체 플레이는 검증하지 않았습니다.
원본 게임 ISO는 포함하지 않습니다.

https://github.com/OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr/releases/tag/v0.8
'''
    (dist/'사용법.txt').write_text(instructions,'utf-8-sig')
    (dist/'HASHES.txt').write_text('\n\n'.join(f"{label}\n크기: {entry['bytes']:,} bytes\nSHA-256: {entry['sha256']}" for label,entry in [('원본 ISO',source),('결과 ISO',target),(patch.name,delta),(exe.name,manifest['patcher'])])+'\n','utf-8-sig')
    archive=dist/f'{PREFIX}-Windows-Patcher.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path in (exe,dist/'사용법.txt',dist/'HASHES.txt'): z.write(path,path.name)
        for path in (ROOT/'licenses').iterdir():
            if path.is_file(): z.write(path,'licenses/'+path.name)
    assets=[(exe.name,exe),(archive.name,archive),(patch.name,patch),('HASHES.txt',dist/'HASHES.txt')]
    manifest['assets']=[dict(name=name,**hashes(path)) for name,path in assets]
    (ROOT/'release-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    sums=''.join(f"{entry['sha256']}  {entry['name']}\n" for entry in manifest['assets'])
    (ROOT/'SHA256SUMS.txt').write_text(sums,'utf8'); (dist/'SHA256SUMS.txt').write_text(sums,'utf8')
    table='| 대상 | 크기 (bytes) | MD5 | SHA-1 | SHA-256 |\n| --- | ---: | --- | --- | --- |\n'
    for label,entry in [('일본판 원본 ISO',source),('v0.8 결과 ISO',target),(exe.name,manifest['patcher']),(patch.name,delta)]:
        table+=f"| {label} | {entry['bytes']:,} | `{entry['md5']}` | `{entry['sha1']}` | `{entry['sha256']}` |\n"
    (ROOT/'HASHES.md').write_text('# v0.8 파일 해시\n\n'+table+'\n## 배포 파일 SHA-256\n\n```text\n'+sums+'```\n','utf8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__': main()
