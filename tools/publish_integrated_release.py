"""Upload and verify the authorized integrated v0.801 release, then update notes."""
import hashlib
import json
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = 'OldManCraveGuitars-bit/XBOX-Genma-Onimusha-Kr'
TAG = 'v0.801'


def gh(*args):
    return subprocess.check_output(['gh', *map(str, args)], cwd=ROOT, text=True, encoding='utf8')


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    manifest = json.loads((ROOT / 'release-manifest-v0.801.json').read_text('utf8'))
    proof = json.loads((ROOT / 'docs/verification/patcher-v0.801.json').read_text('utf8'))
    extra = json.loads((ROOT / 'docs/verification/patcher-extra-v0.801.json').read_text('utf8'))
    assert manifest['windows_exe_roundtrip_verified'] and manifest['iso_content_audit_verified']
    assert proof['status'] == extra['status'] == 'passed'
    assert proof['patcher_sha256'] == extra['patcher_sha256'] == manifest['patcher']['sha256']
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip(), 'Commit source changes first'
    # Source changes and verification records must already be pushed.
    current = json.loads(gh('api', f'repos/{REPO}/commits/main'))['sha']
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert current == head, 'Push verified source and documentation before uploading'
    assets = [(ROOT / ('patches' if a['name'].endswith('.xdelta') else 'dist') / a['name'])
              for a in manifest['assets']]
    assets += [ROOT / 'dist/XBOX-Genma-Onimusha-Kr-v0.801-SHA256SUMS.txt',
               ROOT / 'release-manifest-v0.801.json', ROOT / 'HASHES-v0.801.md',
               ROOT / 'docs/verification/patcher-v0.801.json',
               ROOT / 'docs/verification/patcher-extra-v0.801.json']
    for a in manifest['assets']:
        p = next(p for p in assets if p.name == a['name'])
        assert p.stat().st_size == a['bytes'] and digest(p) == a['sha256']
    print('Uploading verified integrated patcher and hash records', flush=True)
    gh('release', 'upload', TAG, *assets, '--clobber', '--repo', REPO)
    data = json.loads(gh('api', f'repos/{REPO}/releases/tags/{TAG}'))
    remote = {a['name']: a for a in data['assets']}
    verified = []
    for p in assets + [ROOT / 'docs/images' / n for n in ('title.png', 'dialogue.png', 'opening-caption.png')]:
        a = remote[p.name]
        sha = digest(p)
        assert a['size'] == p.stat().st_size and a['digest'] == 'sha256:' + sha
        assert a['state'] == 'uploaded'
        verified.append(dict(name=p.name, bytes=a['size'], sha256=sha))
    print('Uploaded files match local SHA-256; retiring the XBE-only ZIP', flush=True)
    old = 'XBOX-Genma-Onimusha-Kr-v0.801.zip'
    if old in remote:
        gh('release', 'delete-asset', TAG, old, '--yes', '--repo', REPO)
    gh('release', 'edit', TAG, '--title', 'XBOX-Genma-Onimusha-Kr v0.801 · 통합 ISO 패처',
       '--notes-file', ROOT / 'RELEASE_NOTES.md', '--prerelease', '--repo', REPO)
    final = json.loads(gh('api', f'repos/{REPO}/releases/tags/{TAG}'))
    assert not final['draft'] and final['prerelease']
    assert final['body'].startswith('![') and '통합 한글 ISO 한 파일' in final['body']
    assert old not in {a['name'] for a in final['assets']}
    url = next(a['browser_download_url'] for a in final['assets'] if a['name'].endswith('-Windows-Patcher.zip'))
    with urllib.request.urlopen(urllib.request.Request(url, method='HEAD'), timeout=60) as response:
        assert response.status == 200
    record = dict(status='published_and_verified', version=TAG, release_type='integrated single ISO patcher',
                  release_id=final['id'], url=final['html_url'], source_commit=head, prerelease=True,
                  japanese_original_input=True, external_xbe_replacement_required=False,
                  output=manifest['output'], assets=verified, xbe_only_asset_removed=True,
                  physical_xbox_verified=False)
    path = ROOT / 'build/publication-integrated-v0.801.json'
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(record, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
