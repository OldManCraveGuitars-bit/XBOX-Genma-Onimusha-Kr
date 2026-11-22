"""Publish verified stock-XBE data assets, keeping older releases unchanged."""
import hashlib
import json
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO='OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr'


def gh(*args):
    args=list(map(str,args))
    if len(args)>1 and args[0]=='api' and args[1].startswith('repos/'):
        args[1]+=('&' if '?' in args[1] else '?')+'request_nonce='+str(time.time_ns())
    return subprocess.check_output(['gh',*args],cwd=ROOT,text=True,encoding='utf8')


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True,encoding='utf8').strip()


def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    config=json.loads((ROOT/'release-config.json').read_text('utf8'));tag=config['version']
    m=json.loads((ROOT/f'release-manifest-{tag}.json').read_text('utf8'))
    p=json.loads((ROOT/f'docs/verification/patcher-{tag}.json').read_text('utf8'))
    e=json.loads((ROOT/f'docs/verification/patcher-extra-{tag}.json').read_text('utf8'))
    q=json.loads((ROOT/f'docs/verification/stock-xbe-{tag}.json').read_text('utf8'))
    assert m['stock_xbe_unchanged'] and m['windows_exe_roundtrip_verified'] and m['iso_content_audit_verified']
    assert p['status']==e['status']==q['iso']['status']=='passed'
    assert p['patcher_sha256']==e['patcher_sha256']==m['patcher']['sha256']
    assert p['content_audit']['default_xbe_bytes_identical_to_original']
    assert q['iso']['default_xbe_sha256']==config['xbe_sha256']==m['integrated_default_xbe']['sha256']
    assert not git('status','--porcelain'),'Commit verification and source changes first'
    head=git('rev-parse','HEAD')
    assert json.loads(gh('api',f'repos/{REPO}/commits/main'))['sha']==head,'Push main first'
    assert git('rev-parse',tag+'^{commit}')==head,'Tag must point to verified source commit'
    ref=json.loads(gh('api',f'repos/{REPO}/git/ref/tags/{tag}'))
    assert ref['object']['type']=='commit' and ref['object']['sha']==head,'Push the verified lightweight tag first'
    assets=[ROOT/('patches' if a['name'].endswith('.xdelta') else 'dist')/a['name'] for a in m['assets']]
    assets += [ROOT/f'dist/XBOX-Genma-Onimusha-Kr-{tag}-SHA256SUMS.txt',
               ROOT/f'release-manifest-{tag}.json',ROOT/f'HASHES-{tag}.md',
               ROOT/f'docs/verification/patcher-{tag}.json',ROOT/f'docs/verification/patcher-extra-{tag}.json',
               ROOT/f'docs/verification/stock-xbe-{tag}.json',
               ROOT/'docs/images/title.png']
    assets += [ROOT/'docs/verification'/n for n in ('full-stock-xbe-text-proof.png','stock-documents-proof.png','stock-native-captions-proof.png')]
    assert len({p.name for p in assets})==len(assets)
    for a in m['assets']:
        path=next(p for p in assets if p.name==a['name'])
        assert path.stat().st_size==a['bytes'] and sha(path)==a['sha256']
    releases=json.loads(gh('api',f'repos/{REPO}/releases?per_page=100'))
    release=next((r for r in releases if r['tag_name']==tag),None)
    if release is None:
        gh('release','create',tag,'--verify-tag','--draft','--prerelease','--title',
           f'XBOX-Genma-Onimusha-Kr {tag} · 원본 XBE 호환판','--notes-file',ROOT/'RELEASE_NOTES.md','--repo',REPO)
        release=next(r for r in json.loads(gh('api',f'repos/{REPO}/releases?per_page=100')) if r['tag_name']==tag)
    release_id=release['id']
    if release['draft']:
        print('Uploading the verified assets to the draft release',flush=True)
        gh('release','upload',tag,*assets,'--clobber','--repo',REPO)
    else:
        print('Release is already public; checking without replacing assets',flush=True)
    remote=json.loads(gh('api',f'repos/{REPO}/releases/{release_id}'))
    found={a['name']:a for a in remote['assets']};verified=[]
    assert set(found)=={p.name for p in assets},'Unexpected or missing release asset'
    for path in assets:
        asset=found[path.name];digest=sha(path)
        assert asset['size']==path.stat().st_size and asset['digest']=='sha256:'+digest and asset['state']=='uploaded',path.name
        verified.append(dict(name=path.name,bytes=asset['size'],sha256=digest))
    assert remote['body'].strip()==(ROOT/'RELEASE_NOTES.md').read_text('utf8').strip()
    if remote['draft']:
        payload=ROOT/f'build/publish-{tag}.json'
        payload.write_text(json.dumps(dict(draft=False,prerelease=True,make_latest='false')),'utf8')
        print('Uploaded sizes and SHA-256 match; publishing the prerelease',flush=True)
        gh('api','--method','PATCH',f'repos/{REPO}/releases/{release_id}','--input',payload)
    final=json.loads(gh('api',f'repos/{REPO}/releases/{release_id}'))
    assert not final['draft'] and final['prerelease'] and final['tag_name']==tag
    assert final['body'].startswith('![') and '日本語' in final['body'] and config['xbe_sha256'] in final['body']
    assert json.loads(gh('api',f'repos/{REPO}/releases/latest'))['tag_name']=='v0.8'
    url=next(a['browser_download_url'] for a in final['assets'] if a['name'].endswith('-Windows-Patcher.zip'))
    with urllib.request.urlopen(urllib.request.Request(url,method='HEAD'),timeout=60) as response:assert response.status==200
    record=dict(status='published_and_verified',version=tag,release_type=m['release_type'],release_id=release_id,
                url=final['html_url'],download_url=url,source_commit=head,prerelease=True,japanese_original_input=True,
                stock_xbe_unchanged=True,default_xbe_sha256=config['xbe_sha256'],output=m['output'],assets=verified,
                physical_xbox_verified=False,full_gameplay_verified=False)
    (ROOT/f'build/publication-stock-{tag}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(record,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
