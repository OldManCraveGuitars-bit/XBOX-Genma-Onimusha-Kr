"""Create the configured VCDIFF delta from the Japanese original."""
import argparse,hashlib,subprocess
from pathlib import Path
from package_release import ROOT,PREFIX,SOURCE_HASH
import json

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    ap=argparse.ArgumentParser()
    for name in ('source','target','xdelta'):ap.add_argument('--'+name,type=Path,required=True)
    args=ap.parse_args()
    config=json.loads((ROOT/'release-config.json').read_text('utf8'))
    assert sha(args.source)==SOURCE_HASH and sha(args.target)==config['output_sha256']
    destination=ROOT/'patches'/f'{PREFIX}.xdelta';destination.parent.mkdir(exist_ok=True)
    assert not destination.exists(),'Refusing to overwrite an existing delta.'
    subprocess.run([str(args.xdelta),'-e','-6','-A','-D','-B','67108864','-W','16777216','-s',str(args.source),str(args.target),str(destination)],check=True)
    print(destination)

if __name__=='__main__':main()
