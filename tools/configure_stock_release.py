"""Import local CPU/data proofs and pin the v0.802 stock-XBE release hashes."""
import argparse,json,shutil
from pathlib import Path
from disc import Disc
from build_integrated_iso import digests

ROOT=Path(__file__).resolve().parents[1]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True);args=ap.parse_args()
    folder=args.project/'analysis/stock_xbe_compat'
    reports={name:json.loads((folder/file).read_text('utf8')) for name,file in
             [('cpu','verification.json'),('documents','document_verification.json'),('captions','caption_verification.json'),('iso','iso_verification.json')]}
    assert all(v['status']=='passed' for v in reports.values())
    iso=reports['iso'];assert iso['all_original_xbe_extents_untouched'] and iso['default_xbe_directory_record_unchanged']
    original=json.loads((args.project/'analysis/disc_manifest.json').read_text('utf8'))['source']
    disc=Disc(original)
    try:e=next(e for e in disc.entries if e['path']=='default.xbe');offset=e['offset']
    finally:disc.close()
    expected='149f8392db82bbe092ce9b042310373e4645fa898624f57eea55a0c145885216'
    assert iso['default_xbe_sha256']==expected
    config=dict(version='v0.802',assembly_version='0.8.0.2',stock_xbe_unchanged=True,
                source_sha256=iso['source_sha256'],source_bytes=iso['source_bytes'],output_bytes=iso['output_bytes'],
                output_sha256=iso['output_hashes']['sha256'],xbe_bytes=iso['default_xbe_bytes'],xbe_offset=offset,
                xbe_sha256=expected,proof='docs/verification/stock-xbe-v0.802.json',
                workflow='일본판 원본 ISO → 원본 XBE를 유지한 한글 ISO 한 파일.')
    (ROOT/'release-config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n','utf8')
    reports['iso'].pop('output_path',None)
    reports['cpu']={k:v for k,v in reports['cpu'].items() if k not in ('loading','converters')}
    reports.update(version='v0.802',scope='Genma only; Fatal Frame II excluded',stock_xbe_unchanged=True,
                   fixed_ui_rows_retained_in_original_japanese=327,added_opening_movie_and_credit_hooks=False)
    (ROOT/config['proof']).write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n','utf8')
    for name in ('full-stock-xbe-text-proof.png','stock-documents-proof.png','stock-native-captions-proof.png'):
        shutil.copyfile(folder/name,ROOT/'docs/verification'/name)
    (ROOT/'build/stock-xbe-v0.802-target.json').write_text(json.dumps(iso,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(config,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
