"""Publish the verified v0.804 patch assets; preserve every older release."""
import hashlib
import json
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = 'OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr'


def gh(*args):
    args = list(map(str, args))
    if len(args) > 1 and args[0] == 'api' and args[1].startswith('repos/'):
        args[1] += ('&' if '?' in args[1] else '?') + 'request_nonce=' + str(time.time_ns())
    return subprocess.check_output(['gh', *args], cwd=ROOT, text=True, encoding='utf8')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True, encoding='utf8').strip()


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    c = json.loads((ROOT / 'release-config.json').read_text('utf8')); tag = c['version']
    assert tag == 'v0.804' and not c['stock_xbe_unchanged']
    m = json.loads((ROOT / f'release-manifest-{tag}.json').read_text('utf8'))
    p = json.loads((ROOT / f'docs/verification/patcher-{tag}.json').read_text('utf8'))
    extra = json.loads((ROOT / f'docs/verification/patcher-extra-{tag}.json').read_text('utf8'))
    audit = json.loads((ROOT / c['proof']).read_text('utf8'))
    assert m['windows_exe_roundtrip_verified'] and m['iso_content_audit_verified']
    assert p['status'] == extra['status'] == audit['status'] == 'passed'
    assert m['patcher']['sha256'] == p['patcher_sha256'] == extra['patcher_sha256']
    assert m['output']['sha256'] == p['reconstructed_iso_sha256'] == audit['hashes']['sha256']
    assert c['xbe_sha256'] == audit['xbe_sha256'] == p['content_audit']['default_xbe_sha256']
    assert not m['stock_xbe_unchanged'] and not m['xbox360_execution_verified']
    assert not git('status', '--porcelain'), 'Commit source and verification records first'
    head = git('rev-parse', 'HEAD')
    assert json.loads(gh('api', f'repos/{REPO}/commits/main'))['sha'] == head
    assert git('rev-parse', tag + '^{commit}') == head
    ref = json.loads(gh('api', f'repos/{REPO}/git/ref/tags/{tag}'))
    assert ref['object']['type'] == 'commit' and ref['object']['sha'] == head
    assets = [ROOT / ('patches' if a['name'].endswith('.xdelta') else 'dist') / a['name'] for a in m['assets']]
    assets += [ROOT / f'dist/XBOX-Genma-Onimusha-Kr-{tag}-SHA256SUMS.txt',
               ROOT / f'release-manifest-{tag}.json', ROOT / f'HASHES-{tag}.md',
               ROOT / f'docs/verification/patcher-{tag}.json', ROOT / f'docs/verification/patcher-extra-{tag}.json',
               ROOT / f'docs/images/title-{tag}.png']
    assert len({p.name for p in assets}) == len(assets)
    assert all(p.suffix.lower() not in ('.iso', '.xbe', '.xex') and p.stat().st_size < 2**31 for p in assets)
    for a in m['assets']:
        path = next(p for p in assets if p.name == a['name'])
        assert path.stat().st_size == a['bytes'] and sha(path) == a['sha256']
    releases = json.loads(gh('api', f'repos/{REPO}/releases?per_page=100'))
    old_ids = {r['tag_name']: r['id'] for r in releases if r['tag_name'] != tag}
    release = next((r for r in releases if r['tag_name'] == tag), None)
    if release is None:
        gh('release', 'create', tag, '--verify-tag', '--draft', '--prerelease', '--title',
           f'XBOX-Genma-Onimusha-Kr {tag} · 전체 한글화 단일 ISO 패처',
           '--notes-file', ROOT / 'RELEASE_NOTES.md', '--repo', REPO)
        release = next(r for r in json.loads(gh('api', f'repos/{REPO}/releases?per_page=100')) if r['tag_name'] == tag)
    if release['draft']:
        uploaded = {a['name']: a for a in release['assets']}
        pending = [p for p in assets if p.name not in uploaded or uploaded[p.name].get('digest') != 'sha256:' + sha(p)
                   or uploaded[p.name]['size'] != p.stat().st_size]
        if pending:
            print('Uploading verified patch assets to the draft release', flush=True)
            gh('release', 'upload', tag, *pending, '--clobber', '--repo', REPO)
    remote = json.loads(gh('api', f'repos/{REPO}/releases/{release["id"]}'))
    found = {a['name']: a for a in remote['assets']}
    assert set(found) == {p.name for p in assets}
    verified = []
    for path in assets:
        asset = found[path.name]; digest = sha(path)
        assert asset['size'] == path.stat().st_size and asset['digest'] == 'sha256:' + digest and asset['state'] == 'uploaded'
        verified.append(dict(name=path.name, bytes=asset['size'], sha256=digest))
    notes = (ROOT / 'RELEASE_NOTES.md').read_text('utf8').strip()
    assert remote['body'].replace('\r\n', '\n').strip() == notes
    if remote['draft']:
        payload = ROOT / f'build/publish-{tag}.json'
        payload.write_text(json.dumps(dict(draft=False, prerelease=True, make_latest='false')), 'utf8')
        print('All uploaded SHA-256 digests match; publishing prerelease', flush=True)
        gh('api', '--method', 'PATCH', f'repos/{REPO}/releases/{release["id"]}', '--input', payload)
    final = json.loads(gh('api', f'repos/{REPO}/releases/{release["id"]}'))
    assert not final['draft'] and final['prerelease'] and final['tag_name'] == tag
    assert final['body'].startswith('![') and '日本語' in final['body'] and c['xbe_sha256'] in final['body']
    latest_releases = json.loads(gh('api', f'repos/{REPO}/releases?per_page=100'))
    assert all(any(r['tag_name'] == tag_name and r['id'] == rid for r in latest_releases) for tag_name, rid in old_ids.items())
    url = next(a['browser_download_url'] for a in final['assets'] if a['name'].endswith('-Windows-Patcher.zip'))
    with urllib.request.urlopen(urllib.request.Request(url, method='HEAD'), timeout=45) as response:
        assert response.status == 200
    record = dict(status='published_and_verified', version=tag, release_id=final['id'], url=final['html_url'],
                  download_url=url, source_commit=head, prerelease=True, japanese_original_input=True,
                  stock_xbe_unchanged=False, external_runtime_loader_required=False,
                  default_xbe_sha256=c['xbe_sha256'], output=m['output'], assets=verified,
                  pc_cxbx_retail_title_verified=True, physical_xbox_verified=False, xbox360_execution_verified=False,
                  older_releases_preserved=True)
    (ROOT / f'build/publication-single-iso-{tag}.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(record, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
