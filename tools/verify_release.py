"""Verify the configured EXE and independently inspect its complete result ISO."""
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path
from disc import Disc

ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    ap=argparse.ArgumentParser()
    for name in ('source','patched-input','output'):ap.add_argument('--'+name,type=Path,required=True)
    args=ap.parse_args()
    manifest=json.loads((ROOT/'release-manifest.json').read_text('utf8'))
    exe=ROOT/'dist'/manifest['patcher']['name'];assert sha(exe)==manifest['patcher']['sha256']
    cases=[]
    def reject(label,source,output,expected):
        p=subprocess.run([str(exe),'--apply',str(source),str(output)],capture_output=True,text=True,encoding='utf8')
        assert p.returncode!=0 and expected in p.stderr,(label,p.returncode,p.stdout,p.stderr)
        cases.append(dict(name=label,status='passed'))
    with tempfile.TemporaryDirectory(prefix='release-guards-',dir=ROOT/'build') as tmp:
        tmp=Path(tmp);wrong=tmp/'wrong.iso';wrong.write_bytes(b'wrong input');sentinel=tmp/'existing.iso';sentinel.write_bytes(b'preserve me')
        reject('same source and output',wrong,wrong,'원본과 출력 경로')
        reject('existing output preserved',args.source,sentinel,'기존 파일')
        assert sentinel.read_bytes()==b'preserve me' and wrong.read_bytes()==b'wrong input'
        reject('wrong source size',wrong,tmp/'result.iso','원본 크기')
        reject('wrong output extension',args.source,tmp/'result.bin','확장자')
        reject('missing output directory',args.source,tmp/'missing/result.iso','출력 폴더')
        reject('missing source',tmp/'missing.iso',tmp/'result.iso','')
        reject('already patched ISO rejected',args.patched_input,tmp/'result.iso','원본 크기')
        assert not list(tmp.glob('*.partial'))
    output=args.output.resolve()
    assert not output.exists()
    complete=False
    try:
        print('Reconstructing complete ISO using the actual public EXE',flush=True)
        p=subprocess.run([str(exe),'--apply',str(args.source),str(output)],capture_output=True,text=True,encoding='utf8',timeout=900)
        assert p.returncode==0,(p.stdout,p.stderr)
        result=json.loads(p.stdout);assert result['verified'] and result['sha256']==manifest['output']['sha256']
        assert output.stat().st_size==manifest['output']['bytes'] and sha(output)==manifest['output']['sha256']
        assert sha(args.source)==manifest['source']['sha256']
        assert result['version']==manifest['version']
        assert result['stock_xbe_unchanged']==manifest['stock_xbe_unchanged']
        assert result['default_xbe_sha256']==manifest['integrated_default_xbe']['sha256']
        cases.append(dict(name='public EXE complete ISO reconstruction and independent SHA-256',status='passed'))
        source_disc,target_disc=Disc(args.source),Disc(output)
        try:
            old={e['path']:e for e in source_disc.entries};new={e['path']:e for e in target_disc.entries}
            assert old.keys()==new.keys()
            s,t=old['default.xbe'],new['default.xbe']
            a=source_disc.read(s['offset'],s['size']);b=target_disc.read(t['offset'],t['size'])
            assert hashlib.sha256(b).hexdigest()==manifest['integrated_default_xbe']['sha256']
            assert t['size']==manifest['integrated_default_xbe']['bytes']
            assert t['offset']==manifest['integrated_default_xbe']['offset']
            if manifest['stock_xbe_unchanged']:
                assert a==b and s==t
            else:
                import struct
                assert a!=b and struct.unpack_from('<I',b,0x11c)[0]==manifest['integrated_default_xbe']['sections']
                def certificate(x):
                    base=struct.unpack_from('<I',x,0x104)[0]
                    at=struct.unpack_from('<I',x,0x118)[0]-base
                    size=struct.unpack_from('<I',x,at)[0]
                    return x[at:at+size]
                assert certificate(a)==certificate(b)
            content=dict(status='passed',entries=len(old),same_file_and_directory_names=True,
                         default_xbe_bytes_identical_to_original=a==b,
                         default_xbe_directory_record_unchanged=s==t,default_xbe_sha256=hashlib.sha256(b).hexdigest(),
                         original_certificate_preserved=True,
                         full_iso_hash_matches_independently_audited_target=True)
        finally:source_disc.close();target_disc.close()
        cases.append(dict(name='disc entries, expected XBE and original certificate; complete ISO hash verified',status='passed'))
        report=dict(status='passed',cases=cases,source_preserved=True,original_iso_sha256=manifest['source']['sha256'],
                    reconstructed_iso_sha256=manifest['output']['sha256'],reconstructed_bytes=output.stat().st_size,
                    patcher_sha256=manifest['patcher']['sha256'],content_audit=content,game_runtime_tested=False)
        version=manifest['version']
        (ROOT/f'docs/verification/patcher-{version}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
        for path in (ROOT/'release-manifest.json',ROOT/f'release-manifest-{version}.json',ROOT/f'dist/release-manifest-{version}.json'):
            data=json.loads(path.read_text('utf8'))
            data.update(windows_exe_roundtrip_verified=True,guards_passed=7,iso_content_audit_verified=True)
            path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
        complete=True
        print(json.dumps(report,ensure_ascii=False,indent=2))
    finally:
        # Only the exact temporary output created by this test is removed.
        if not complete and output.exists():output.unlink()

if __name__=='__main__':main()
